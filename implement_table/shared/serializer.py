from mongoengine.fields import FloatField
from rest_framework.fields import BooleanField, CharField
from rest_framework_mongoengine.serializers import EmbeddedDocumentSerializer, DocumentSerializer
from implement_table.core.fields import BDateField, BDynamicField, BEmbeddedListField
from implement_table.shared.models import AttachedFile, DocumentState, BillingDocument, BillingList, Modality, Bank, PaymentModeType, \
    Currency, Tariff


class AttachedFileSerializer(EmbeddedDocumentSerializer):
    class Meta:
        model = AttachedFile
        fields = []


class DocumentStateSerializer(EmbeddedDocumentSerializer):
    is_archived = BooleanField(default=False)
    archived_at = BDateField()
    is_closed = BooleanField(default=False)
    closed_at = BDateField()
    is_draft = BooleanField(default=True)
    is_valid = BooleanField(default=False)

    class Meta:
        model = DocumentState
        fields = ['is_archived', 'archived_at', 'is_closed', 'closed_at', 'is_draft', 'is_valid']


class BillingDocumentSerializer(DocumentSerializer):
    beneficiary = BDynamicField(required=True)
    comment = CharField(required=False, allow_null=True)
    doc_date = BDateField()
    attached_files = BEmbeddedListField(serializer=AttachedFileSerializer, allow_null=True, required=False)
    states = DocumentStateSerializer(required=False, allow_null=True)

    class Meta:
        model = BillingDocument
        fields = ['id', 'number', 'beneficiary', 'comment', 'doc_date', 'attached_files', 'states']


class CurrencySerializer(DocumentSerializer):
    class Meta:
        model = Currency
        fields = ['id', 'full_name', 'short_name', 'fraction_name', 'fraction_link_word', 'is_default']


class BillingListSerializer(DocumentSerializer):
    class Meta:
        model = BillingList
        fields = []


class ModalitySerializer(BillingListSerializer):
    class Meta:
        model = Modality
        fields = BillingListSerializer.Meta.fields + []


class BankSerializer(BillingListSerializer):
    class Meta:
        model = Bank
        fields = BillingListSerializer.Meta.fields + []


class PaymentModeTypeSerializer(BillingListSerializer):
    class Meta:
        model = PaymentModeType
        fields = BillingListSerializer.Meta.fields + []


class TariffSerializer(EmbeddedDocumentSerializer):
    tm = FloatField(default=0)
    tp = FloatField(default=0)

    class Meta:
        model = Tariff
        fields = ("tm", "tp")
