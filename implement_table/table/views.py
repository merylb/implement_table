from implement_table.core.classes import BViewSet
from implement_table.table.serializer import TableConfigSerializer


class TableConfigViewSet(BViewSet):
    serializer_class = TableConfigSerializer
