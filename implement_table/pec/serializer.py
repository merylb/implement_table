from mongoengine.fields import FloatField
from rest_framework.fields import CharField
from rest_framework_mongoengine.serializers import EmbeddedDocumentSerializer

from implement_table.core.fields import BEmbeddedListField
from implement_table.pec.models import CareRequestAnswer, CareRequest, CareRequestLine
from implement_table.shared.serializer import BillingDocumentSerializer


class CareRequestLineSerializer(EmbeddedDocumentSerializer):
    code = CharField(allow_null=True, required=False, allow_blank=True)
    quotation = FloatField(default=0)
    qte = FloatField(default=0)

    class Meta:
        model = CareRequestLine
        fields = ['code', 'quotation', 'qte']


class CareRequestAnswerSerializer(EmbeddedDocumentSerializer):
    quotation = FloatField(default=0)
    description = CharField(allow_null=True, required=False, allow_blank=True)
    ref = CharField(allow_null=True, required=False, allow_blank=True)
    type = CharField(allow_null=True, required=False, allow_blank=True)

    class Meta:
        model = CareRequestAnswer
        fields = ['quotation', 'description', 'ref',
                  'type']


class CareRequestSerializer(BillingDocumentSerializer):
    details = BEmbeddedListField(serializer=CareRequestLineSerializer, allow_null=True, required=False)
    answers = BEmbeddedListField(serializer=CareRequestAnswerSerializer, allow_null=True, required=False)

    class Meta:
        model = CareRequest
        fields = BillingDocumentSerializer.Meta.fields + ['details', 'answers']
