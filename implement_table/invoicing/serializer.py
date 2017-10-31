from rest_framework.fields import FloatField, BooleanField, CharField
from rest_framework_mongoengine.serializers import EmbeddedDocumentSerializer
from implement_table.core.fields import BDynamicField, BEmbeddedListField, BDateField
from implement_table.invoicing.models import InvoicingDocument, DetailLine, InvoiceLine, Invoice, FeesNote
from implement_table.shared.serializer import BillingDocumentSerializer, TariffSerializer


class InvoicingDocumentSerializer(BillingDocumentSerializer):
    beneficiary_name = CharField(read_only=True)
    taxed_amount = FloatField(read_only=True)
    text_amount = CharField(read_only=True)
    remaining_amount = FloatField(read_only=True)
    paid_amount = FloatField(read_only=True)
    is_paid = BooleanField(read_only=True)
    payment_status = CharField(read_only=True)

    class Meta:
        model = InvoicingDocument
        fields = BillingDocumentSerializer.Meta.fields + ['beneficiary_name', 'taxed_amount', 'text_amount',
                                                          'remaining_amount',
                                                          'paid_amount', 'is_paid', 'payment_status']


class DetailLineSerializer(EmbeddedDocumentSerializer):
    code = CharField(required=False)
    description = CharField(required=True)
    discount = FloatField(default=0)
    unit_price = FloatField(default=0)
    qte = FloatField(default=0)
    tariff = TariffSerializer(required=False, allow_null=True)
    line_doc = BDynamicField()
    is_comment = BooleanField(default=False)

    total_amount = FloatField(read_only=True)
    discount_amount = FloatField(read_only=True)

    class Meta:
        model = DetailLine
        fields = ['code', 'description', 'discount', 'unit_price', 'qte', 'tariff', 'line_doc', 'is_comment',
                  'total_amount', 'discount_amount']


class InvoiceLineSerializer(EmbeddedDocumentSerializer):
    details = BEmbeddedListField(serializer=DetailLineSerializer, allow_null=True, required=False)
    description = CharField()
    is_comment = BooleanField(default=False)
    line_doc = BDynamicField(allow_null=True,required=False)

    class Meta:
        model = InvoiceLine
        fields = ['details', 'description', 'is_comment', 'line_doc']


class InvoiceSerializer(InvoicingDocumentSerializer):
    beneficiary_type = CharField()
    tariff = TariffSerializer(required=True, allow_null=True)
    lines = BEmbeddedListField(serializer=InvoiceLineSerializer, allow_null=True, required=False)

    class Meta:
        model = Invoice
        fields = InvoicingDocumentSerializer.Meta.fields + ['beneficiary_type', 'tariff', 'lines']


class FeesNoteSerializer(InvoicingDocumentSerializer):
    lines = BEmbeddedListField(serializer=DetailLineSerializer, allow_null=True, required=False)
    payment_deadline = BDateField(allow_null=True,required=False)

    class Meta:
        model = FeesNote
        fields = InvoicingDocumentSerializer.Meta.fields + ['lines', 'payment_deadline']
