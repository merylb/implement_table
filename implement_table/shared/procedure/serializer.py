from rest_framework.fields import CharField, BooleanField, FloatField, ListField
from rest_framework_mongoengine.serializers import DocumentSerializer, EmbeddedDocumentSerializer

from implement_table.core.fields import BReferenceField
from implement_table.shared.procedure.models import NGAPCode, CCAMCode, Procedure, ProcedureCatalog
from implement_table.shared.serializer import ModalitySerializer


class NGAPCodeSerializer(EmbeddedDocumentSerializer):
    key = CharField(required=False, allow_null=True)

    class Meta:
        model = NGAPCode
        fields = ['key']


class CCAMCodeSerializer(EmbeddedDocumentSerializer):
    key = CharField(required=False, allow_null=True)

    class Meta:
        model = CCAMCode
        fields = ['key']


class ProcedureSerializer(DocumentSerializer):
    code = CharField()
    name = CharField()
    price = FloatField(required=False)
    is_refundable = BooleanField(required=False)
    NGAP_code = NGAPCodeSerializer(NGAPCode)
    CCAM_code = CCAMCodeSerializer(CCAMCode)
    modality = BReferenceField(serializer=ModalitySerializer, required=False)
    tnr = FloatField(required=False)

    class Meta:
        model = Procedure
        fields = ("id", "name", "code", "price", "is_refundable", "NGAP_code", "CCAM_code", "modality", "tnr")


class ProcedureCatalogSerializer(DocumentSerializer):
    is_default = BooleanField(default=False)
    procedures = ListField(child=BReferenceField(serializer=ProcedureSerializer, required=False, allow_null=True),
                           required=False,
                           allow_null=True)

    class Meta:
        model = ProcedureCatalog
        fields = ("id", "name", "is_default", "procedures")
