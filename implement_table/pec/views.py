from implement_table.pec.serializer import CareRequestSerializer
from implement_table.core.classes import BViewSet


class CareRequestViewSet(BViewSet):
    serializer_class = CareRequestSerializer
