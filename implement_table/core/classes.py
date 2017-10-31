import logging
from datetime import datetime

from bson.dbref import DBRef
from bson.objectid import ObjectId
from camel_snake_kebab import snake_case, kebab_case
from django.http.response import Http404
from mongoengine.document import Document
from mongoengine.fields import SequenceField, DateTimeField, BooleanField, IntField, ReferenceField
from mongoengine.queryset.manager import QuerySetManager
from mongoengine.queryset.queryset import QuerySet
from rest_framework import viewsets, permissions
from rest_framework.routers import SimpleRouter, Route, DynamicListRoute, DynamicDetailRoute
from rest_framework.response import Response
from mongoengine import signals

from implement_table.core.decorators import singleton
from implement_table.core.utils import get_class


class BQuerySet(QuerySet):
    def erase(self, write_concern=None, _from_doc_delete=False,
              cascade_refs=None):
        super(BQuerySet, self).delete(write_concern=write_concern, _from_doc_delete=_from_doc_delete,
                                      cascade_refs=cascade_refs)

    def delete(self, parent_level=None, write_concern=None):
        queryset = parents = self.clone()
        doc = queryset._document

        has_delete_signal = signals.signals_available and (
            signals.pre_delete.has_receivers_for(doc) or signals.post_delete.has_receivers_for(doc)
        )

        if has_delete_signal:
            pass

        query = {
            "set__is_deleted": True,
            "set__deleted_at": datetime.now()
        }

        level = doc.DELETING_LEVEL if parent_level is None else parent_level

        if level is not None:
            parent_ids = [item.id for item in parents]
            query['deleting_level'] = level
            parent_query = {doc.delete_by(): {"$in": parent_ids}, "is_deleted": {"$ne": True}}
            for child in doc.DELETING_CHILDS:
                model_ = get_class(child)
                model_.objects(**parent_query).delete(parent_level=parent_level)

        result = queryset.update(**query)
        return result if result else 0

    def restore(self, parent_level=None):
        queryset = parents = self.clone()
        doc = queryset._document

        query = {
            "set__is_deleted": False,
            "unset__deleted_at": 1,
            "unset__deleting_level": 1
        }

        level = doc.DELETING_LEVEL if parent_level is None else parent_level

        if level is not None:
            parent_ids = [item.id for item in parents]
            parent_query = {doc.delete_by(): {"$in": parent_ids}, "deleting_level": level}
            for child in doc.DELETING_CHILDS:
                model_ = get_class(child)
                model_.objects(**parent_query).restore(parent_level=parent_level)

        result = queryset.update(**query)
        return result if result else 0

    def aggregate(self, *pipeline, **kwargs):
        items = super(BQuerySet, self).aggregate(*pipeline, **kwargs)
        return list(items)

    def get_order_by(self, *attrs, **kwargs):
        return self._get_order_by(*attrs, **kwargs)


class BQuerySetManager(QuerySetManager):
    default = BQuerySet


class BDocument(Document):
    DELETING_LEVEL = None
    DELETING_CHILDS = ()

    id = SequenceField(primary_key=True)
    created_at = DateTimeField(default=None)
    updated_at = DateTimeField(default=None)
    deleted_at = DateTimeField(default=None)
    is_deleted = BooleanField(default=False)
    deleting_level = IntField(default=None)
    is_system = BooleanField(default=None)

    # owner = ReferenceField('Staff', null=True)  # 2017-09-24

    _serializer = None
    default_serializer = None

    all = BQuerySetManager()
    objects = BQuerySetManager()

    meta = {
        'abstract': True
    }

    def __eq__(self, other):
        return getattr(self, 'id', None) == getattr(other, 'id', None)

    def __new__(cls, **kwargs):
        cls._fields['id'].owner_document = cls
        if cls.default_serializer is None:
            cls.default_serializer = cls.__name__ + "Serializer"

        """
        signals.post_init.connect(document.post_init, sender=cls)
        signals.post_init.connect(document.post_init, sender=cls)
        signals.pre_save.connect(document.pre_save, sender=cls)
        signals.pre_save_post_validation.connect(document.pre_save_post_validation, sender=cls)
        signals.post_save.connect(document.post_save, sender=cls)
        signals.pre_delete.connect(document.pre_delete, sender=cls)
        signals.post_delete.connect(document.post_delete, sender=cls)
        signals.pre_bulk_insert.connect(document.pre_bulk_insert, sender=cls)
        signals.post_bulk_insert.connect(document.post_bulk_insert, sender=cls)
        signals.pre_init.connect(document.pre_init, sender=cls)
        """

        return super(BDocument, cls).__new__(cls)

    def save(self, **kwargs):
        if self.created_at is None:
            self.created_at = datetime.now()
        else:
            self.updated_at = datetime.now()

        return super(BDocument, self).save(**kwargs)

    def erase(self, signal_kwargs=None, **write_concern):
        super(BDocument, self).delete(signal_kwargs=signal_kwargs, **write_concern)

    def delete(self, parent_level=None, **write_concern):
        self.is_deleted = True
        self.deleted_at = datetime.now()

        level = self.DELETING_LEVEL if parent_level is None else parent_level

        if level is not None:
            self.deleting_level = level
            for child in self.DELETING_CHILDS:
                model_ = get_class(child)
                query = {self.delete_by(): self, "is_deleted": {"$ne": True}}
                model_.objects(**query).delete(parent_level=level)

        return self.save()

    def restore(self, parent_level=None):
        self.is_deleted = False
        del self.deleted_at
        del self.deleting_level

        level = self.DELETING_LEVEL if parent_level is None else parent_level

        if level is not None:
            for child in self.DELETING_CHILDS:
                model_ = get_class(child)
                query = {self.delete_by(): self, "deleting_level": level}
                model_.objects(**query).restore(parent_level=level)

        return self.save()

    @classmethod
    def to_ref_cls(cls, pk):
        return DBRef(cls._get_collection_name(), pk)

    @classmethod
    def dynamic_field_ref(cls, pk):
        return {'_ref': cls.to_ref_cls(pk), '_cls': cls.__name__}

    @classmethod
    def delete_by(cls):
        return snake_case(cls.__name__)

    @classmethod
    def from_son(cls, data, created=False):
        return cls._from_son(data, created=created)

    @property
    def serializer(self):
        if self._serializer is None:
            names = self.__class__.__module__.split('.')
            names.pop()
            names.append("serializer")

            mod = __import__(".".join(names), fromlist=self.default_serializer)
            self._serializer = getattr(mod, self.default_serializer)

        return self._serializer

    """
    #@todo add queryset
    #@queryset_manager
    #def objects(self, queryset):
    #    return queryset.filter(__raw__={"is_deleted": {"$ne": True}})
    """


class BPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user

        if not user.is_authenticated():
            return False
        elif user.profile.is_root:
            return True
        elif view.resource in user.profile.permissions:
            if user.profile.permissions[view.resource].is_all:
                return True
            else:
                method = request.method.lower()
                actions = user.profile.permissions[view.resource].actions
                request_kwargs = request.__dict__['parser_context']['kwargs']

                if method not in ["post", "put"]:
                    return method in actions.keys() and actions[method] != 'none'
                elif "pk" in request_kwargs:
                    return "update" in actions and actions['update'] != 'none'
                else:
                    return "create" in actions and actions['create'] != 'none'

    def has_object_permission(self, request, view, obj):
        self.has_permission(request, view)


class BViewSet(viewsets.ModelViewSet):
    pk = None
    logger = None
    serializer_class = None
    # permission_classes = (BPermission,)
    resource = None
    owner_fields = ('owner',)
    order_by = ()

    def __init__(self, **kwargs):
        if self.resource is None:
            self.resource = kebab_case(self.get_model().__name__)

        super(BViewSet, self).__init__(**kwargs)

    @classmethod
    def urls(cls) -> object:
        mn_router = BRouter()
        mn_router.register(r'^', cls, cls.__name__)
        return mn_router.urls

    def get_model(self):
        return self.serializer_class.Meta.model

    def get_object(self):
        try:
            self.pk = int(self.kwargs["pk"])
        except ValueError:
            self.pk = ObjectId(self.kwargs["pk"])

        try:
            query = {"_id": self.pk, "is_deleted": {"$ne": True}}

            query.update(self.permission_filter())

            query = self.hidden_model_filter(query)

            return self.get_model().objects.get(__raw__=query)

        except self.get_model().DoesNotExist:
            raise Http404

    def get_objects(self):
        query = {"is_deleted": {"$ne": True}}

        query.update(self.permission_filter())

        query = self.hidden_model_filter(query, many=True)
        return self.get_model().objects(__raw__=query).order_by(*self.order_by)

    def hidden_model_filter(self, query=None, many=False):
        return {}

    def permission_filter(self):
        return {}

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_objects(), many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        return super(BViewSet, self).retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        if request.staff is not None:
            request.data['owner'] = {"id": request.staff.id}

        return super(BViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        # TODO : fix the log if file in it
        """self.logger.info({
            "user": request.user,
            "message": "update <" + self.get_model().__name__ + "> with id: " + kwargs["pk"] + ", data: " + json.dumps(
                request.data)
        })"""

        #  print(self.get_serializer(data=request.data).context['request'].staff, self.get_object())

        return super(BViewSet, self).update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        return super(BViewSet, self).partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return super(BViewSet, self).destroy(request, *args, **kwargs)


class BRouter(SimpleRouter):
    routes = [
        # List route.
        Route(
            url=r'^{prefix}{trailing_slash}$',
            mapping={
                'get': 'list',
                'post': 'create'
            },
            name='{basename}-list',
            initkwargs={'suffix': 'List'}
        ),
        # Dynamically generated list routes.
        # Generated using @list_route decorator
        # on methods of the viewset.
        DynamicListRoute(
            url=r'^{prefix}/{methodname}{trailing_slash}$',
            name='{basename}-{methodnamehyphen}',
            initkwargs={}
        ),
        # Detail route.
        Route(
            url=r'^{prefix}/{lookup}{trailing_slash}$',
            mapping={
                'get': 'retrieve',
                'post': 'update',
                'put': 'partial_update',
                'delete': 'destroy'
            },
            name='{basename}-detail',
            initkwargs={'suffix': 'Instance'}
        ),
        # Dynamically generated detail routes.
        # Generated using @detail_route decorator on methods of the viewset.
        DynamicDetailRoute(
            url=r'^{prefix}/{lookup}/{methodname}{trailing_slash}$',
            name='{basename}-{methodnamehyphen}',
            initkwargs={}
        ),
    ]


@singleton
class BConfig:
    def __init__(self):
        from  implement_table.shared.config.models import BillingConfig

        self._datetime_format = BillingConfig.get_by_key("datetime_format")
        self._date_format = BillingConfig.get_by_key("date_format")
        self._time_format = BillingConfig.get_by_key("time_format")
        self._lang = BillingConfig.get_by_key("lang")
        self._currency_float = BillingConfig.get_by_key("currency_float")
        self._precise_float = BillingConfig.get_by_key("precise_float")

    @property
    def datetime_format(self):
        if self._datetime_format is None:
            return "%Y-%m-%d"
        else:
            return self._datetime_format.value['py']

    @property
    def date_format(self):
        if self._date_format is None:
            return "%Y-%m-%d"
        else:
            return self._date_format.value['py']

    @property
    def time_format(self):
        if self._time_format is None:
            return "%Y-%m-%d"
        else:
            return self._time_format.value['py']

    @property
    def datetime_formats_tuple(self):
        return self.datetime_format, "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S.%fZ"

    @property
    def date_formats_tuple(self):
        return self.date_format, "%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S.%fZ"

    @property
    def time_formats_tuple(self):
        return self.time_format, "%H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M", "%Y-%m-%dT%H:%M:%S.%fZ"

    @property
    def lang(self):
        if self._lang is None:
            return "fr"
        else:
            return self._lang

    @property
    def currency_float(self):
        if self._currency_float is None:
            return 2
        else:
            return self._currency_float.value

    @property
    def precise_float(self):
        if self._precise_float is None:
            return 2
        else:
            return self._precise_float.value
