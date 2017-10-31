from implement_table.core.classes import BViewSet
from implement_table.payment.serializer import PaymentSerializer


class PaymentViewSet(BViewSet):
    serializer_class = PaymentSerializer
