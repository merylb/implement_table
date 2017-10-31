from rest_framework.fields import CharField, FloatField
from rest_framework_mongoengine.serializers import EmbeddedDocumentSerializer

from implement_table.core.fields import BReferenceField, BDateField, BDynamicField, BEmbeddedListField
from implement_table.payment.models import PaymentMode, Payment, PaymentLine
from implement_table.shared.serializer import BillingDocumentSerializer, BankSerializer, PaymentModeTypeSerializer


class PaymentModeSerializer(EmbeddedDocumentSerializer):
    ref = CharField(default="")
    bank = BReferenceField(serializer=BankSerializer, required=False, allow_null=True)
    type = BReferenceField(serializer=PaymentModeTypeSerializer, required=False, allow_null=True)

    class Meta:
        model = PaymentMode
        fields = ['ref', 'bank', 'type']


class PaymentLineSerializer(EmbeddedDocumentSerializer):
    total_amount = FloatField(required=False)
    encasement_amount = FloatField(required=False)
    paid_doc = BDynamicField(allow_null=True,required=False)

    class Meta:
        model = PaymentLine
        fields = ['encasement_amount', 'paid_doc', 'total_amount', 'remaining_amount']


class PaymentSerializer(BillingDocumentSerializer):
    beneficiary_type = CharField(allow_blank=True, allow_null=True)
    deadline = BDateField(allow_null=True,required=False)
    payer = BDynamicField(allow_null=True,required=False)
    payer_type = CharField(allow_blank=True, allow_null=True)
    received_amount = FloatField(default=0)
    payment_mode = PaymentModeSerializer(allow_null=True, required=False)
    lines = BEmbeddedListField(serializer=PaymentLineSerializer, allow_null=True, required=False)

    consumed_amount = FloatField(read_only=True)
    remaining_amount = FloatField(read_only=True)
    payer_name = CharField(read_only=True)
    beneficiary_name = CharField(read_only=True)

    class Meta:
        model = Payment
        fields = BillingDocumentSerializer.Meta.fields + ['beneficiary_type', 'deadline', 'payer', 'payer_type',
                                                          'received_amount', 'payment_mode', 'consumed_amount',
                                                          'remaining_amount', 'payer_name', 'beneficiary_name', 'lines']
