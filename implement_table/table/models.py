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
    order_by = StringField(required=True)
    is_orderable = BooleanField(default=False)
    is_searchable = BooleanField(default=False)
    is_editable = BooleanField(default=False)
    is_required = BooleanField(default=False)
    is_global_searchable = BooleanField(default=False)
    is_ref = BooleanField(default=False)
    module = StringField(default=None)
    model = StringField(default=None)
    rounded = BooleanField(default=False)
    is_callable = BooleanField(default=False)

    show_in = EmbeddedDocumentListField(AllowPropertyNamespace)

    order_in = EmbeddedDocumentListField(ValuePropertyNamespace)
    is_icon = BooleanField(default=False)
    icon_name = StringField()

    style_classes = EmbeddedDocumentListField(TableClasses)


class PaginationNamespace(EmbeddedDocument):
    name = StringField()
    page_size = IntField()
    page_options = ListField(IntField(), unique=True)


class Table(EmbeddedDocument):
    columns = EmbeddedDocumentListField(TableColumns)
    pagination = EmbeddedDocumentListField(PaginationNamespace)
    classes = EmbeddedDocumentListField(TableClasses)
    filtered_by_owner = BooleanField(default=False)


class TableConfig(BaseConfig):
    value = EmbeddedDocumentField(Table)
