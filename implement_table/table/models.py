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
    unit = StringField(default=None)
    order_by = StringField(default='')
    is_orderable = BooleanField(default=False)
    is_searchable = BooleanField(default=False)
    is_editable = BooleanField(default=False)
    is_required = BooleanField(default=False)
    is_global_searchable = BooleanField(default=False)

    rounded = BooleanField(default=False)
    is_callable = BooleanField(default=False)

    show_in = EmbeddedDocumentListField(AllowPropertyNamespace,
                                        default=[AllowPropertyNamespace(**{"name": "default", "allow": True})])
    order_in = EmbeddedDocumentListField(ValuePropertyNamespace,
                                         default=[ValuePropertyNamespace(**{"name": "default", "value": 0})])
    # is_icon = BooleanField(default=False)
    icon_name = StringField()

    is_extended = BooleanField(default=False)
    colspan = IntField(default=1)
    style_classes = EmbeddedDocumentListField(TableClasses)

    # TO REMOVE
    is_ref = BooleanField(default=False)
    module = StringField(default=None)
    model = StringField(default=None)


class PaginationNamespace(EmbeddedDocument):
    name = StringField()
    page_size = IntField()
    page_options = ListField(IntField(), unique=True)


class SharedGroup(EmbeddedDocument):
    user = DynamicField()
    access = ListField(StringField)
    is_owner = BooleanField(default=False)
    is_favorite = BooleanField(default=False)


class ViewQuery(EmbeddedDocument):
    column = StringField()
    operator = StringField()
    value = DynamicField()
    logical_operator = StringField()


class TableView(EmbeddedDocument):
    shared_group = EmbeddedDocumentListField(SharedGroup)
    name = StringField(required=True)
    model = StringField(required=True)
    is_default = BooleanField(default=False)
    access = StringField(default='public')
    query = ListField(ViewQuery)


class Table(EmbeddedDocument):
    columns = EmbeddedDocumentListField(TableColumns)
    pagination = EmbeddedDocumentListField(PaginationNamespace, default=[
        PaginationNamespace(**{'name': 'default', 'page_size': 5, 'page_options': [5, 10, 20, 30]})])
    classes = EmbeddedDocumentListField(TableClasses)
    filtered_by_owner = BooleanField(default=False)
    view = EmbeddedDocumentField(TableView)


class TableConfig(BaseConfig):
    value = EmbeddedDocumentField(Table)
