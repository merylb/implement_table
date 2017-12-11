import ujson
from datetime import datetime, timedelta
from tempfile import mktemp

import pydash
import xlsxwriter
from mongoengine import BooleanField, DateTimeField
from mongoengine.fields import ReferenceField
from pydash.collections import filter_, reduce_
from pydash.objects import get
from rest_framework.response import Response

# from App.core.classes import MnConfig
# from App.shared.config.models import TableConfig, TableColumns
# from App.shared.staff.models import Staff
# from App.ws.messages import WsFile

from implement_table.shared.staff.models import Staff
from implement_table.table.models import TableConfig, TableColumns
from implement_table.ws.messages import WsFile


class MnRetrieveEventMixin:
    def get(self, data, **kwargs):
        subscriber = kwargs.get('subscriber')

        if "pk" in data:
            obj = self.get_object(data.get('pk'), subscriber.user, subscriber.staff)

            return self.get_serializer(obj).data
        else:
            return self.get_serializer(self.get_objects(subscriber.user, subscriber.staff), many=True).data


class MnConfigEventMixin:
    @classmethod
    def _get_owner(cls, user):
        try:
            return Staff.objects.get(user=user)
        except Staff.DoesNotExist:
            return None

    def get_config(self, data, **kwargs):
        mine = data.pop('mine', False)

        if mine:
            owner = kwargs.get('subscriber').staff
        else:
            owner = None

        result = list()
        for key in data['keys']:
            obj = self.get_model().get_by_key(key, owner)
            result.append(obj)

        return self.get_serializer(result, many=True).data

    def set_config(self, data, **kwargs):
        mine = data.pop('mine', False)

        if mine:
            owner = kwargs.get('subscriber').staff
        else:
            owner = None

        model_class = self.get_model()

        for key, value in data['config'].items():

            try:
                instance = model_class.get_by_key_and_owner(key, owner)
                self._update_value(instance, value)

            except model_class.DoesNotExist:
                model_class(key=key, value=value, owner=owner).save()

        return True

    def _new_value(self, key, value):
        pass

    def _update_value(self, instance, value):
        data = dict()
        data['value'] = value
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()


class MnTableEventMixin:
    def list(self, data, **kwargs):
        dictionary = {}
        query = {
            "$and": []
        }

        if "search_all" in data and data["search_all"] != "":
            search_keys = []
            columns = list(filter(lambda x: x.is_global_searchable, self._get_columns()))
            search_values = data["search_all"].split(' ')

            for column in columns:
                for k in search_values:
                    if not column.is_ref and self._generate_query(column, k) is not None:
                        search_keys.append(self._generate_query(column, k))
                    elif column.is_ref and self._generate_reference_query(column, k) is not None:
                        search_keys.append(self._generate_reference_query(column, k))

            if search_keys:
                query["$and"].append({'$or': search_keys})

        if "search" in data:
            search_keys = []
            columns = self._get_columns()

            for key in data["search"].keys():
                if data["search"][key] != "" and data["search"][key] is not None:
                    column = list(filter(lambda x: x.order_by == key, columns))
                    if len(column) > 0:
                        column = column[0]
                        if not column.is_ref and self._generate_query(column, data["search"][key]) is not None:
                            search_keys.append(self._generate_query(column, data["search"][key]))
                        elif column.is_ref and self._generate_reference_query(column, data["search"][key]) is not None:
                            search_keys.append(self._generate_reference_query(column, data["search"][key]))
                    else:
                        search_keys.append({key: data["search"][key]})

            if search_keys:
                query["$and"].append({'$and': search_keys})

        query["$and"] += self._handle_access(kwargs)

        page = self.get_model().objects(__raw__=query) if len(query['$and']) > 0 else self.get_model().objects

        offset = (data["page"] - 1) * data["limit"]
        dictionary["length"] = page.count()

        if dictionary["length"] < offset:
            offset = 0

        dictionary["list"] = self.get_serializer(page.skip(offset).limit(data["limit"]).order_by(data["order"]),
                                                 many=True).data

        return dictionary

    def get_config(self, data, **kwargs):
        from implement_table.table.serializer import TableSerializer
        mine = data.pop('mine', False)

        if mine:
            owner = self._get_owner(kwargs['subscriber'].user)
        else:
            owner = None

        return TableSerializer(TableConfig.get_by_key(self.config_key, owner).value).data

    def _get_columns(self):
        return TableConfig.get_by_key(self.config_key, None).value.columns

    def _filtered_by_owner(self):
        return TableConfig.get_by_key(self.config_key, None).value.filtered_by_owner

    @staticmethod
    def _generate_query(column, search_key, key=None):
        from implement_table.core.classes import BConfig
        key = column.order_by if key is None else key

        if column.type == "text" or column.type == "time":
            return {key: {'$regex': '.*' + search_key + '.*', '$options': 'i'}}
        if column.type == "number":
            return {key: {'$eq': float(search_key)}}
        if column.type == "date":
            try:
                _date = datetime.strptime(search_key, BConfig().date_format)
                return {key: {'$gte': _date, '$lt': _date + timedelta(days=1)}}
            except ValueError:
                pass

        return None

    def _generate_reference_query(self, column, value):
        mod = __import__("App." + column.module + ".models", fromlist=column.model)
        model = getattr(mod, column.model)
        keys = column.order_by.split('.')
        if self._generate_query(column, value, key=keys[-1]) is not None:
            q = self._generate_query(column, value, key=keys[-1])
            list_ = [x.id for x in model.objects(__raw__=q).all().only('id')]
            key = (keys[0] if len(keys) == 2 else '.'.join(keys[:-1]))
            return {key: {'$in': list_}}

        return None

    def _handle_access(self, kwargs):
        q = []

        if self._filtered_by_owner:
            subscriber = kwargs.get("subscriber")
            owner_ = self.permission_filter(subscriber.user, subscriber.staff, "get")
            q.append(owner_)

        if MnHiddenModelMixin in self.get_model().mro():
            hidden_ = self.hidden_model_filter(kwargs.get("subscriber").user)
            q.append(hidden_)

        return q

    def update_columns(self, data, **kwargs):
        from implement_table.table.serializer import TableSerializer
        owner = None

        _d = []
        for value in data:
            _d.append(TableColumns(**value))

        config = TableConfig.get_by_key(self.config_key, owner)
        config.value.columns = _d
        config.save()
        return TableSerializer(config.value).data

    def generate_excel(self, data, **kwargs):
        from implement_table.core.classes import BConfig
        columns = self._get_columns()
        columns = filter_(columns, lambda x: x.is_shown)
        excel_body = self._generate_excel_body_items(columns, kwargs)

        file_temp = "{}.xlsx".format(mktemp())

        wb = xlsxwriter.Workbook(file_temp, {'constant_memory': True})
        worksheet = wb.add_worksheet(data.get('page_name'))

        # TODO add more validations on the header of the excel (search and order by)
        for index, column in enumerate(columns):
            if column.type == "date":
                format_t = {'num_format': get(BConfig(), '_date_format.value.js')}
                fmt = wb.add_format(format_t)
                worksheet.set_column(0, index, 12, fmt)
            else:
                worksheet.set_column(0, index, 30)

            value = get(data, column.label)
            worksheet.write(0, index, value)

        for row, items in enumerate(excel_body):
            worksheet.write_row(row + 1, 0, items)

        wb.close()

        with open(file_temp, 'rb') as file:
            body = file.read()

        generated_at = datetime.now().strftime(BConfig().date_format)

        return WsFile(body=body, name="{}-{}.xlsx".format(data.get('file_name'), generated_at))

    def _generate_excel_body_items(self, columns, kwargs):
        def handle_items_reduce(items_, item):
            def handle_columns_reduce(total, column):
                value_ = get(item, column.order_by) if get(item, column.label) is None else get(item, column.label)
                total.append(value_)
                return total

            value = reduce_(columns, iteratee=handle_columns_reduce, accumulator=[])
            items_.append(value)

            return items_

        query = {
            "is_deleted": {"$ne": True}
        }

        access_level = self._handle_access(kwargs)

        if len(access_level) > 0:
            query["$and"] = access_level

        items = self.get_model().objects(__raw__=query)

        items = reduce_(items, iteratee=handle_items_reduce, accumulator=[])

        return items


class MnAutoCompleteSearchEventMixin:
    def search(self, data, **kwargs):
        field = data.get('field', '')
        q = ".*{}.*".format(data.get('query', ''))

        query = {field: {'$regex': q, '$options': 'i'}}
        objects = self.get_model().objects(__raw__=query).limit(10)
        serializer = self.get_serializer(objects, many=True)
        return serializer.data


class MnHistoryEventMixin:
    date_field = "created_at"
    reference_field = None
    version_serializer = None

    def active_version(self, data, **kwargs):
        from implement_table.core.classes import BConfig
        reference_id = data.pop(self.reference_field)

        date_ = get(data, 'max_date', None)

        query = {
            self.reference_field: int(reference_id),
        }

        if date_ is not None:
            query[self.date_field] = {"$lt": datetime.strptime(date_, BConfig().date_format) + timedelta(days=1)}

        subscriber = kwargs.get('subscriber')
        query.update(self.permission_filter(subscriber.user, subscriber.staff, 'get'))

        sort = [
            {'$match': query},
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": "%Y-%m-%d",
                            "date": "${}".format(self.date_field)
                        }
                    },
                    "pk": {"$last": "$_id"},
                    "created_at": {"$last": "${}".format(self.date_field)}}
            },
            {'$sort': {self.date_field: -1}},
            {'$limit': 1},
            {"$project": {"_id": "$pk"}}
        ]

        object__ = self.get_model().objects.aggregate(*sort)

        if len(object__) > 0:
            pk = get(object__, '0._id')
            object__ = self.get_model().objects.get(id=pk)

            serializer = self.get_serializer(object__)

            return serializer.data
        else:
            return dict()

    def versions(self, data, **kwargs):
        reference_id = data.pop(self.reference_field)

        query = {
            self.reference_field: int(reference_id),
        }

        subscriber = kwargs.get('subscriber')
        query.update(self.permission_filter(subscriber.user, subscriber.staff, 'get'))

        sort = [
            {'$match': query},
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": "%Y-%m-%d",
                            "date": "$created_at"
                        }
                    },
                    "pk": {"$last": "$_id"},
                    "created_at": {"$last": "$created_at"}}
            },
            {"$project": {"_id": "$pk", self.date_field: 1}},
            {'$sort': {self.date_field: -1}},
        ]

        items = self.get_model().objects.aggregate(*sort)

        if len(items) > 0:
            items = [self.get_model().from_son(item, created=True) for item in items]

            serializer = self.version_serializer(items, many=True)

            return serializer.data
        else:
            return []


class MnLastVersionViewSetMixin:
    key_field = "$key"
    date_field = "$created_at"

    def get_objects(self):
        match = {"is_deleted": {"$ne": True}}
        match.update(self.permission_filter())

        group = {"_id": self.key_field, "pk": {"$last": "$_id"}, "creation_date": {"$last": self.date_field}}
        items = self.get_model().objects.aggregate({'$match': match}, {"$group": group})

        object__ = sorted(items, key=lambda item: item.get('pk'))

        return [self.get_model().objects.get(id=item.get('pk')) for item in object__]


class MnDisabledSetMixin:
    def get_objects(self):
        flag = self.request.query_params.get('flag', True)

        flag = flag if isinstance(flag, bool) else ujson.loads(flag)

        query = {"is_deleted__ne": True}

        if flag:
            query['is_disabled__ne'] = True

        return self.get_model().objects(**query).order_by(*self.order_by)


class MnValidationModelMixin:
    is_validated = BooleanField(default=False)
    validate_at = DateTimeField(default=None)


class MnHiddenModelMixin:
    is_hidden = BooleanField(default=False)
    hidden_at = DateTimeField(default=None)
    hidden_by = ReferenceField('Staff', null=True)


class MnHiddenVisitMixin:
    @property
    def is_hidden(self):
        self.visit.is_hidden


class UniqueFieldValidationMixin:
    unique_field = "title"

    def title_validation(self, data, **kwargs):
        query = {self.unique_field: data['value'], "is_deleted__ne": True}

        if 'id' in data and data['id'] is not None:
            query['id__ne'] = data['id']

        try:
            self.get_model().objects.get(**query)
        except self.get_model().DoesNotExist:
            return True
        except self.get_model().MultipleObjectsReturned:
            return False
        else:
            return False


class MnContextSerializerMixin:
    def get_context(self):
        top_level_context = getattr(self, "_top_level_context", None)
        if top_level_context is None:
            return self.root.context
        else:
            return top_level_context

    def get_staff(self):
        return pydash.get(self.get_context(), "request.staff", None)

    def get_user(self):
        return pydash.get(self.get_context(), "request.user", None)


class MnHasOwnerSerializerMixin(MnContextSerializerMixin):
    def save(self, **kwargs):
        is_new_instance = self.instance is None
        instance = super(MnHasOwnerSerializerMixin, self).save(**kwargs)

        if is_new_instance:
            instance.owner = self.get_staff()
            instance.save()

        return instance


class MnHiddenSerializerMixin(MnContextSerializerMixin):
    def save(self, **kwargs):
        is_new_instance = self.instance is None
        instance = super(MnHiddenSerializerMixin, self).save(**kwargs)

        user = self.get_user()
        staff = self.get_staff()
        if getattr(user, 'is_special', False) and is_new_instance:
            instance.is_hidden = True
            instance.hidden_by = staff
            instance.hidden_at = datetime.now()
            instance.save()

        return instance


class MnDynamicEmbeddedDocument:
    _serializer = None
    default_serializer = None

    def __new__(cls, *args, **kwargs):
        cls.default_serializer = "{}Serializer".format(cls.__name__)
        return super(MnDynamicEmbeddedDocument, cls).__new__(cls)

    @property
    def serializer(self):
        if self._serializer is None:
            names = self.__class__.__module__.split('.')
            names.pop()
            names.append("serializer")

            mod = __import__(".".join(names), fromlist=self.default_serializer)
            self._serializer = getattr(mod, self.default_serializer)

        return self._serializer


class MnListByReference:
    def get_objects(self, reference_id=None):
        query = {"is_deleted": {"$ne": True}}

        query.update(self.permission_filter())

        query = self.hidden_model_filter(query, many=True)

        if reference_id is not None:
            query[self.reference_field] = reference_id

        return self.get_model().objects(__raw__=query).order_by(*self.order_by)

    def list(self, request, **kwargs):
        reference_id = request.GET.get(self.reference_field, None)

        self.logger.info({
            "user": request.user,
            "message": "retrieve list of <" + self.get_model().__name__ + "> <<by " + self.reference_field + ">>"
        })

        serializer = self.get_serializer(self.get_objects(int(reference_id)), many=True)
        return Response(serializer.data)
