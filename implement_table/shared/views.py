from implement_table.core.classes import BViewSet
from implement_table.shared.insurance.serializer import OrganizationSerializer
from implement_table.shared.procedure.serializer import ProcedureSerializer


class ProcedureViewSet(BViewSet):
    serializer_class = ProcedureSerializer


class OrganizationViewSet(BViewSet):
    serializer_class = OrganizationSerializer
