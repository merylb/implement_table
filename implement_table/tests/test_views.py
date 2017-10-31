from django.test import TestCase, Client
from implement_table.invoicing.models import Invoice
from implement_table.invoicing.serializer import InvoiceSerializer
from rest_framework import status


class InvoiceViewTestCase(TestCase):
    """ Test views """

    def setUp(self):
        self.client = Client()
        self.assertEqual(type(self.client), Client)

    def test_get(self):
        response = self.client.get('/api/invoice/')
        invoices = Invoice.objects.all()
        serializer = InvoiceSerializer(invoices, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
