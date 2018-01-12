from mongoengine.document import EmbeddedDocument
from mongoengine.fields import StringField, DynamicField, BooleanField, IntField, EmbeddedDocumentListField, \
    EmbeddedDocumentField, ListField
from mongoengine import queryset_manager

from implement_table.core.classes import BDocument


class BaseConfig(BDocument):
    key = StringField(required=True)
    value = DynamicField()
    # speciality = ReferenceField(MedicalSpeciality, required=False, default=None, null=True)
    # owner = ReferenceField(Staff, required=False, default=None, null=True)
    meta = {'abstract': True}

    @queryset_manager
    def _get_by_key_only(self, queryset, key, create=False):
        try:
            return queryset.filter().get(key=key)
        except self.DoesNotExist:
            if create:
                return self(key=key).save()
            else:
                return None

    @queryset_manager
    def get_by_key_and_owner(self, queryset, key, owner):
        return queryset.filter().get(key=key)

    @queryset_manager
    def _get_by_key_and_speciality(self, queryset, key, owner):
        return queryset.filter().get(key=key)

    @classmethod
    def get_by_key(cls, key, owner=None, create=False):
        if owner is None:
            return cls._get_by_key_only(key, create=create)
        else:
            try:
                return cls.get_by_key_and_owner(key, owner)
            except cls.DoesNotExist:
                try:
                    return cls._get_by_key_and_speciality(key, owner)
                except cls.DoesNotExist:
                    return cls._get_by_key_only(key, create=create)


class AllowPropertyNamespace(EmbeddedDocument):
    name = StringField()
    allow = BooleanField()


class ValuePropertyNamespace(EmbeddedDocument):
    name = StringField()
    value = IntField()


class TableClasses(EmbeddedDocument):
    css_class = StringField()
    key = StringField()
    opposite = BooleanField()


class TableColumns(EmbeddedDocument):
    label = StringField(required=True)
    name = StringField(required=True)
    type = StringField(default="text")
    description = StringField(default=None)
    unit = StringField(default='')
    order_by = StringField(default='')
    is_orderable = BooleanField(default=False)
    is_searchable = BooleanField(default=False)
    is_editable = BooleanField(default=False)
    is_required = BooleanField(default=False)
    is_global_searchable = BooleanField(default=False)
    rounded = BooleanField(default=False)
    is_callable = BooleanField(default=False)

    show_in = EmbeddedDocumentListField(AllowPropertyNamespace)
    order_in = EmbeddedDocumentListField(ValuePropertyNamespace)
    icon_name = StringField()
    is_extended = BooleanField(default=False)
    colspan = IntField(default=1)
    style_classes = EmbeddedDocumentListField(TableClasses)

    def __init__(self, *args, **kwargs):
        if not kwargs.get('order_in'):
            kwargs['order_in'] = [ValuePropertyNamespace(**{"name": "default", "value": 0})]
        if not kwargs.get('show_in'):
            kwargs['show_in'] = [AllowPropertyNamespace(**{"name": "default", "allow": True})]
        super(EmbeddedDocument, self).__init__(*args, **kwargs)


class PaginationNamespace(EmbeddedDocument):
    name = StringField()
    page_size = IntField()
    page_options = ListField(IntField(), unique=True)


class Table(EmbeddedDocument):
    columns = EmbeddedDocumentListField(TableColumns)
    pagination = EmbeddedDocumentListField(PaginationNamespace)
    classes = EmbeddedDocumentListField(TableClasses)
    filtered_by_owner = BooleanField(default=False)

    def __init__(self, *args, **kwargs):
        if not kwargs.get('pagination'):
            kwargs['pagination'] = [
                PaginationNamespace(**{'name': 'default', 'page_size': 5, 'page_options': [5, 10, 20, 30]})]
        super(EmbeddedDocument, self).__init__(*args, **kwargs)


class TableConfig(BaseConfig):
    value = EmbeddedDocumentField(Table)
