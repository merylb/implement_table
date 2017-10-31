from django.test import TestCase

from implement_table.invoicing.models import Invoice
from implement_table.payment.models import Payment


class InvoiceTestCase(TestCase):
    def setUp(self):
        if len(Invoice.objects(number="xxx")) == 0:
            Invoice.objects.create(number="xxx")

    def test_get(self):
        inv = Invoice.objects.get(number="xxx")
        self.assertEqual(inv.number, 'xxx')

    def test_delete(self):
        Invoice.objects.get(number="xxx").delete()
        self.assertEqual(len(Invoice.objects(number="xxx", is_deleted=False)), 0)


class PaymentTestCase(TestCase):
    def setUp(self):
        if len(Payment.objects(number="pppp")) == 0:
            Payment.objects.create(number="pppp")

    def test_get(self):
        p = Payment.objects.get(number="pppp")
        self.assertEqual(p.number, 'pppp')
