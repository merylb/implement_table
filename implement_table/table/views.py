from pydash import py_
from rest_framework.response import Response

from implement_table.core.classes import BViewSet

from implement_table.table.mixins import MnTableMixin

from . import serializer


class TableConfigViewSet(BViewSet, MnTableMixin):
    serializer_class = serializer.TableConfigSerializer

    _model_serializer = None
    _model = None
    configKey = None

    def create(self, request, *args, **kwargs):
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

        return Response(self.request_list(_query, _order, confi_key))
