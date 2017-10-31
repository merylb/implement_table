from mongoengine.document import EmbeddedDocument
from mongoengine.fields import StringField, DateTimeField, DynamicField, FloatField, EmbeddedDocumentField, \
    ReferenceField, EmbeddedDocumentListField
from implement_table.shared.models import Bank, PaymentModeType, BillingDocument


class PaymentMode(EmbeddedDocument):
    ref = StringField(null=True, default="")
    bank = ReferenceField(Bank)
    type = ReferenceField(PaymentModeType)


class PaymentLine(EmbeddedDocument):
    encasement_amount = FloatField(required=True)
    total_amount = FloatField(required=True)
    paid_doc = DynamicField()
    remaining_amount = FloatField()


class Payment(BillingDocument):
    beneficiary_type = StringField()
    deadline = DateTimeField()
    payer = DynamicField()
    payer_type = StringField()
    received_amount = FloatField(default=0)
    payment_mode = EmbeddedDocumentField(PaymentMode)
    lines = EmbeddedDocumentListField(PaymentLine)

    @property
    def consumed_amount(self):
        return sum(line.encasement_amount for line in self.lines)

    @property
    def remaining_amount(self):
        return self.received_amount - self.consumed_amount

    @property
    def payer_name(self):
        return self.payer.complete_name

    @property
    def beneficiary_name(self):
        return self.beneficiary.complete_name
