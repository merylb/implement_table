from pydash import py_
from rest_framework.response import Response

from implement_table.core.classes import BViewSet

from implement_table.table.mixins import MnTableMixin
from implement_table.table.models import TableConfig, Table, TableColumns, PaginationNamespace
from implement_table.table.serializer import TableSerializer, TableConfigSerializer, TableColumnsSerializer

from . import serializer
from implement_table.invoicing.serializer import InvoiceSerializer


class TableConfigViewSet(BViewSet, MnTableMixin):
    serializer_class = serializer.TableConfigSerializer

    _model_serializer = None
    _model = None
    configKey = None

    def first_config(self, request):
        model = request.data.pop('model', "")
        serializer = request.data.pop('serializer', "")
        confi_key = request.data.pop('configKey', "")
        pkg = request.data.pop('packaging', "")
        _query = request.data.pop('query', {})
        _order = request.data.pop('sorting', {})

        serializer_pkg = __import__("{}{}".format(pkg, '.serializer'), fromlist=serializer + 'Serializer')
        model_pkg = __import__("{}{}".format(pkg, '.models'), fromlist=model)
        model_class = getattr(model_pkg, model)
        serializer_class = getattr(serializer_pkg, serializer + 'Serializer')
        self._model = model_class
        self._model_serializer = serializer_class
        print('tetetetee------------', self.request_list(_query, _order, confi_key))
        return Response(self.request_list(_query, _order, confi_key))

    def last_config(self, request):

        model = request.data.pop('model', "")
        confi_key = request.data.pop('configKey', "")
        pkg = request.data.pop('package', "")
        _query = request.data.pop('query', {})
        _order = request.data.pop('sorting', {})

        serializer_pkg = __import__("{}{}".format(pkg, '.serializer'), fromlist=model + 'Serializer')
        model_pkg = __import__("{}{}".format(pkg, '.models'), fromlist=model)
        model_class = getattr(model_pkg, model)
        serializer_class = getattr(serializer_pkg, model + 'Serializer')
        self._model = model_class
        self._model_serializer = serializer_class

        return Response(self.request_list(_query, _order, model))

    def create(self, request, *args, **kwargs):
        if request.data.pop('serializer', ""):
            return self.first_config(request)
        else:
            return self.last_config(request)


class TableConfig2ViewSet(BViewSet, MnTableMixin):
    serializer_class = serializer.TableConfigSerializer

    def create(self, request, *args, **kwargs):
        config_key = request.data.pop('configKey', "")
        config = request.data.pop('config', "")
        columns = list()
        # **{'name': 'default', 'page_size': 5, 'page_options': [5, 10, 20, 30]}))
        for item in config['columns']:
            column = TableColumns(**item)
            columns.append(column)

        table_config = TableConfig.get_by_key(config_key)
        table = Table(columns=columns)

        if table_config is None:
            # table.pagination.append(
            #     PaginationNamespace(**{'name': 'default', 'page_size': 5, 'page_options': [5, 10, 20, 30]}))
            table_config = TableConfig(key=config_key, value=table)
        else:
            table.pagination = table_config.value.pagination
            table_config.value = table
        table_config.save(validate=False)

        return Response(TableConfigSerializer(table_config).data)


class TableFilterViewSet(BViewSet, MnTableMixin):
    serializer_class = serializer.TableConfigSerializer

    def create(self, request, *args, **kwargs):
        print('teteette----------------', request.data)
        return Response('testtttttttttttttttttttttttt')


class TableViewForColumns(BViewSet, MnTableMixin):
    serializer_class = InvoiceSerializer
    config_key = "Invoice"
    model = "invoicing.Invoice"

    def create(self, request, *args, **kwargs):
        method_name = request.data.get('event_method_name')
        quey = request.data.get('query', {})
        exec_func = getattr(self, method_name)
        return Response(exec_func(**quey))


class TableViewSet(BViewSet, MnTableMixin):
    serializer_class = TableConfigSerializer
