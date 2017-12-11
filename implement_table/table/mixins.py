from datetime import datetime, timedelta

from pydash import py_
from pydash.collections import find

from implement_table.core.classes import BConfig
from implement_table.table.models import TableConfig, TableColumns
import re


class MnTableMixin:
    def split_properties_fields(self, search_keys):
        model_fields = self._model._fields.keys()

        property_fields = py_(search_keys).filter_(
            lambda item: any(k not in model_fields for k in item.keys())
        ).value()
        search_keys = py_(search_keys).reject(
            lambda item: any(k not in model_fields for k in item.keys())
        ).value()
        p_fields = {k: d[k] for d in property_fields for k in d.keys()}
        return search_keys, p_fields

    @staticmethod
    def filter_by_properties(p_fields, page):
        p_keys = sorted(p_fields.keys())
        for p in p_keys:
            if '$regex' in p_fields[p].keys():
                res = py_(page).filter_(
                    lambda item: re.compile(p_fields[p]['$regex'], re.IGNORECASE).search(getattr(item, p))).value()
            elif '$eq' in p_fields[p].keys():
                res = py_(page).filter_(
                    lambda item: p_fields[p]['$eq'] == getattr(item, p)).value()
            page = res if len(res) > 0 or p == p_keys[-1] else page
        return page

    def request_list(self, data, order, configKey):
        dictionary = {}
        query = {
            "$and": []
        }

        data_order = order.pop('sort_by', 'id')
        order_direction = order.pop('direction', '-').replace('asc', '+').replace('desc', '-');
        search_filter = data.pop('filter', {})
        config_value = TableConfig.get_by_key(configKey, None).value
        pagination = find(config_value.pagination, lambda item: item.name == data['namespace']) or find(
            config_value.pagination, lambda
                item: item.name == 'default')
        search_keys = []
        if "multi_search" in search_filter and len(search_filter["multi_search"]) > 0:

            columns = self._get_columns(configKey)
            for col in search_filter["multi_search"]:
                column = list(filter(lambda x: x.order_by == col['column'], columns))
                if len(column) > 0:
                    column = column[0]
                    if not column.is_ref and self._generate_query(column, col['value']) is not None:
                        search_keys.append(self._generate_query(column, col['value']))
                    elif column.is_ref and self._generate_reference_query(column, col['value']) is not None:
                        search_keys.append(self._generate_reference_query(column, col['value']))
                else:
                    search_keys.append({col['column']: col['value']})
            print('tttttttttttttttttttttt', search_keys)

        if "search_all" in search_filter and search_filter["search_all"] != "":
            search_keys = []
            columns = list(filter(lambda x: x.is_global_searchable, self._get_columns(configKey)))
            search_values = search_filter["search_all"].split(' ')
            for column in columns:
                for k in search_values:
                    if not column.is_ref and self._generate_query(column, k) is not None:
                        search_keys.append(self._generate_query(column, k))
                    elif column.is_ref and self._generate_reference_query(column, k) is not None:
                        search_keys.append(self._generate_reference_query(column, k))

        search_keys, p_fields = self.split_properties_fields(search_keys)

        if search_keys:
            query["$and"].append({'$or': search_keys})
        # query["$and"] += self._handle_access(kwargs)
        page = self._model.objects(__raw__=query) if len(query['$and']) > 0 else self._model.objects
        offset = (data["page"]) * pagination['page_size']
        dictionary["length"] = page.count()
        if dictionary["length"] < offset:
            offset = 0
        page = page.skip(offset).limit(pagination['page_size']).order_by('{}{}'.format(order_direction, data_order))
        if p_fields:
            page = self.filter_by_properties(p_fields, page)
        dictionary["list"] = self._model_serializer(page, many=True).data
        return dictionary

    # def get_config(self, data, **kwargs):
        # mine = data.pop('mine', False)
        # if mine:
        #     owner = self._get_owner(kwargs['subscriber'].user)
        # else:
        #     owner = None
        # TableConfig.get_by_key(configKey, None).value
        # return TableConfig.get_by_key(self.config_key, owner).value


    @staticmethod
    def _get_columns(config_key):
        return TableConfig.get_by_key(config_key, None).value.columns

    #

    # def _filtered_by_owner(self):
    #     return TableConfig.get_by_key(self.config_key, None).value.filtered_by_owner
    #
    @staticmethod
    def _generate_query(column, search_key, key=None):
        key = column.name if key is None else key

        if column.type == "text" or column.type == "time":
            return {key: {'$regex': '.*' + search_key + '.*', '$options': 'i'}}
        if column.type == "number":
            return {key: {'$eq': float(search_key)}}
        if column.type == "date":
            try:
                _date = datetime.strptime(search_key, BConfig().date_format)
                return {key: {'$gte': _date, '$lt': _date + timedelta(days=1)}}
            except ValueError as ex:
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
        #

    # def _handle_access(self, kwargs):
    #     q = []
    #
    #     if self._filtered_by_owner:
    #         subscriber = kwargs.get("subscriber")
    #         owner_ = self.permission_filter(subscriber.user, subscriber.staff, "get")
    #         q.append(owner_)
    #
    #     if MnHiddenModelMixin in self.get_model().mro():
    #         hidden_ = self.hidden_model_filter(kwargs.get("subscriber").user)
    #         q.append(hidden_)
    #
    #     return q

    def update_columns(self, data, **kwargs):
        from . import serializer
        owner = None

        _d = []
        for value in data:
            _d.append(TableColumns(**value))

        config = TableConfig.get_by_key(self.config_key, owner)
        config.value.columns = _d
        config.save()
        return serializer.TableSerializer(config.value).data

        # def generate_excel(self, data, **kwargs):
        #     columns = self._get_columns()
        #     columns = filter_(columns, lambda x: x.is_shown)
        #     excel_body = self._generate_excel_body_items(columns, kwargs)
        #
        #     file_temp = "{}.xlsx".format(mktemp())
        #
        #     wb = xlsxwriter.Workbook(file_temp, {'constant_memory': True})
        #     worksheet = wb.add_worksheet(data.get('page_name'))
        #
        #     # TODO add more validations on the header of the excel (search and order by)
        #     for index, column in enumerate(columns):
        #         if column.type == "date":
        #             format_t = {'num_format': get(MnConfig(), '_date_format.value.js')}
        #             fmt = wb.add_format(format_t)
        #             worksheet.set_column(0, index, 12, fmt)
        #         else:
        #             worksheet.set_column(0, index, 30)
        #
        #         value = get(data, column.label)
        #         worksheet.write(0, index, value)
        #
        #     for row, items in enumerate(excel_body):
        #         worksheet.write_row(row + 1, 0, items)
        #
        #     wb.close()
        #
        #     with open(file_temp, 'rb') as file:
        #         body = file.read()
        #
        #     generated_at = datetime.now().strftime(MnConfig().date_format)
        #
        #     return WsFile(body=body, name="{}-{}.xlsx".format(data.get('file_name'), generated_at))
        #
        # def _generate_excel_body_items(self, columns, kwargs):
        #     def handle_items_reduce(items_, item):
        #         def handle_columns_reduce(total, column):
        #             value_ = get(item, column.order_by) if get(item, column.label) is None else get(item, column.label)
        #             total.append(value_)
        #             return total
        #
        #         value = reduce_(columns, iteratee=handle_columns_reduce, accumulator=[])
        #         items_.append(value)
        #
        #         return items_
        #
        #     query = {
        #         "is_deleted": {"$ne": True}
        #     }
        #
        #     access_level = self._handle_access(kwargs)
        #
        #     if len(access_level) > 0:
        #         query["$and"] = access_level
        #
        #     items = self.get_model().objects(__raw__=query)
        #
        #     items = reduce_(items, iteratee=handle_items_reduce, accumulator=[])
        #
        #     return items
