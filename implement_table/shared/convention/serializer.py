from rest_framework.fields import CharField
from rest_framework_mongoengine.serializers import DocumentSerializer, EmbeddedDocumentSerializer

from implement_table.core.fields import BReferenceField, BEmbeddedListField
from implement_table.shared.convention.models import ConventionException, Convention
from implement_table.shared.models import Tariff
from implement_table.shared.procedure.serializer import ProcedureSerializer
from implement_table.shared.serializer import TariffSerializer


class ConventionExceptionSerializer(EmbeddedDocumentSerializer):
    procedure = BReferenceField(serializer=ProcedureSerializer)
    tariff = TariffSerializer(Tariff)

    class Meta:
        model = ConventionException
        fields = ("procedure", "tariff")


class ConventionSerializer(DocumentSerializer):
    label = CharField(required=False)
    tariff = TariffSerializer(Tariff)
    exceptions = BEmbeddedListField(serializer=ConventionExceptionSerializer, required=False, allow_null=True)

    class Meta:
        model = Convention
        fields = ("id", "label", "tariff", "exceptions")
