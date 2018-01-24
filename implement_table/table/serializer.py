from implement_table.core.fields import BEmbeddedListField, BDynamicField

from rest_framework.fields import CharField, BooleanField, IntegerField, ListField, ChoiceField
from rest_framework_mongoengine.serializers import EmbeddedDocumentSerializer, DocumentSerializer

from implement_table.table.models import Table, TableConfig, TableClasses, ValuePropertyNamespace, TableColumns, \
    AllowPropertyNamespace, PaginationNamespace, SharedGroup, ViewQuery, TableView


class TableClassesSerializer(EmbeddedDocumentSerializer):
    class Meta:
        model = TableClasses
        fields = "__all__"


class AllowPropertyNamespaceSerializer(EmbeddedDocumentSerializer):
    name = CharField(required=True)
    allow = BooleanField(default=True)

    class Meta:
        model = AllowPropertyNamespace
        fields = "__all__"


class ValuePropertyNamespaceSerializer(EmbeddedDocumentSerializer):
    name = CharField(required=True)
    value = IntegerField(default=0)

    class Meta:
        model = ValuePropertyNamespace
        fields = "__all__"


class TableColumnsSerializer(EmbeddedDocumentSerializer):
    label = CharField()
    name = CharField()
    type = CharField()
    description = CharField(default='', allow_null=True)
    unit = CharField(allow_null=True, allow_blank=True)
    order_by = CharField(required=False, allow_blank=True)
    is_orderable = BooleanField(default=False)
    is_searchable = BooleanField(default=False)
    is_editable = BooleanField(default=False)
    is_global_searchable = BooleanField(default=False)
    is_required = BooleanField(default=False)
    is_ref = BooleanField(default=False)
    module = CharField(default=None, allow_null=True)
    model = CharField(default=None, allow_null=True)
    rounded = BooleanField(default=False, required=False)

    show_in = BEmbeddedListField(serializer=AllowPropertyNamespaceSerializer, required=False, allow_null=True)
    order_in = BEmbeddedListField(serializer=ValuePropertyNamespaceSerializer, required=False, allow_null=True)

    icon_name = CharField(required=False, allow_blank=True, allow_null=True)
    is_extended = BooleanField(default=False)
    colspan = IntegerField(default=1)
    style_classes = BEmbeddedListField(serializer=TableClassesSerializer, required=False, allow_null=True)

    class Meta:
        model = TableColumns
        fields = "__all__"


class PaginationNamespaceSerializer(EmbeddedDocumentSerializer):
    name = CharField()
    page_size = IntegerField()
    page_options = ListField(child=IntegerField(), required=False, default=[5, 10, 15, 20])

    class Meta:
        model = PaginationNamespace
        fields = ('name', 'page_size', 'page_options')


class SharedGroupSerializer(EmbeddedDocumentSerializer):
    user = BDynamicField()
    access = ListField(child=CharField())
    is_owner = BooleanField(default=False)

    class Meta:
        model = SharedGroup
        fields = '__all__'


class ViewQuerySerializer(EmbeddedDocumentSerializer):
    column = CharField()
    operator = CharField()
    value = BDynamicField()
    logical_operator = CharField()

    class Meta:
        model = ViewQuery
        fields = '__all__'


class TableViewSerializer(EmbeddedDocumentSerializer):
    shared_group = BEmbeddedListField(serializer=SharedGroupSerializer)
    name = CharField(required=True)
    model = CharField(required=True)
    is_default = BooleanField(default=False)
    access = ChoiceField(choices=['private', 'public', 'restrict'], required=False)
    query = ListField(child=ViewQuerySerializer(many=False, read_only=False, allow_null=True, required=False))

    class Meta:
        model = TableView
        fields = '__all__'


class TableSerializer(EmbeddedDocumentSerializer):
    columns = BEmbeddedListField(serializer=TableColumnsSerializer, sorted_by=True)
    classes = BEmbeddedListField(serializer=TableClassesSerializer)
    filtered_by_owner = BooleanField(default=False)
    view = TableViewSerializer(many=False, read_only=False, allow_null=True, required=True)
    pagination = BEmbeddedListField(serializer=PaginationNamespaceSerializer, required=False)

    class Meta:
        model = Table
        fields = ('columns', 'classes', 'filtered_by_owner', 'pagination', 'view')


class TableConfigSerializer(DocumentSerializer):
    key = CharField(required=True)
    value = TableSerializer(many=False, read_only=False, allow_null=True, required=True)

    class Meta:
        model = TableConfig
        fields = ['id', 'value', 'key']
