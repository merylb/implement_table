from implement_table.core.classes import BViewSet
from implement_table.invoicing.serializer import InvoiceSerializer, FeesNoteSerializer


class InvoiceViewSet(BViewSet):
    serializer_class = InvoiceSerializer


class FeesNoteViewSet(BViewSet):
    serializer_class = FeesNoteSerializer
