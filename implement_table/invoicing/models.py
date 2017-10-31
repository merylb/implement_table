from mongoengine.document import EmbeddedDocument
from mongoengine.fields import StringField, EmbeddedDocumentField, EmbeddedDocumentListField, BooleanField, FloatField, \
    DynamicField, DateTimeField
from pydash import py_
from implement_table.payment.models import Payment
from implement_table.shared.models import BillingDocument, Tariff
from implement_table.shared.utils import amount_to_text, PaymentStatus


class InvoicingDocument(BillingDocument):
    @property
    def beneficiary_name(self):
        return getattr(self, "beneficiary").complet_name

    @property
    def taxed_amount(self):
        return round(sum([detail.total_amount for detail in self.lines]), 2)

    @property
    def text_amount(self):
        return amount_to_text(self.taxed_amount)

    @property
    def remaining_amount(self):
        return self.taxed_amount - self.paid_amount

    @property
    def paid_amount(self):
        return py_(py_(Payment.objects(is_deleted=False, lines__paid_doc=self)).map(
            lambda item: item.lines).flatten().filter(lambda elt: elt.paid_doc == self).value()).map_(
            lambda item: item.encasement_amount).sum().value()

    @property
    def is_paid(self):
        return self.taxed_amount - self.paid_amount == 0

    @property
    def payment_status(self):
        if self.is_closed:
            return PaymentStatus.is_exempt
        elif self.is_paid:
            return PaymentStatus.is_paid
        elif self.paid_amount > 0:
            return PaymentStatus.is_partial_paid
        else:
            return PaymentStatus.is_unpaid

    meta = {'abstract': True}


class DetailLine(EmbeddedDocument):
    code = StringField(required=False)
    description = StringField()
    discount = FloatField(default=0)
    unit_price = FloatField(default=0)
    qte = FloatField(default=0)
    tariff = EmbeddedDocumentField(Tariff)
    line_doc = DynamicField()
    is_comment = BooleanField(default=False)

    @property
    def total_amount(self):
        return (self.unit_price * self.qte) - self.discount_amount

    @property
    def discount_amount(self):
        return (self.unit_price * self.qte) * self.discount / 100


class InvoiceLine(EmbeddedDocument):
    details = EmbeddedDocumentListField(DetailLine)
    description = StringField()
    is_comment = BooleanField()
    line_doc = DynamicField()


class Invoice(InvoicingDocument):
    beneficiary_type = StringField()
    tariff = EmbeddedDocumentField(Tariff)
    lines = EmbeddedDocumentListField(InvoiceLine)


class FeesNote(InvoicingDocument):
    lines = EmbeddedDocumentListField(DetailLine)
    payment_deadline = DateTimeField()
