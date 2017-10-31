from mongoengine.document import EmbeddedDocument
from mongoengine.fields import StringField
from rest_framework import serializers
from rest_framework_mongoengine.fields import DynamicField
from operator import attrgetter

from implement_table.core.classes import BConfig, BDocument
from implement_table.core.utils import get_model_class, get_class


class BDateField(serializers.DateTimeField):
    def __init__(self, **kwargs):
        super(BDateField, self).__init__(BConfig().date_format, BConfig().date_formats_tuple, **kwargs)


class BDynamicField(DynamicField):
    def __init__(self, **kwargs):
        super(BDynamicField, self).__init__(StringField, **kwargs)

    def to_representation(self, obj):
        if isinstance(obj, (BDocument, EmbeddedDocument)):
            data = obj.serializer(obj).data
            data['_module'] = obj.__class__.__module__
            data['_model'] = obj.__class__.__name__
            return data

        return super(BDynamicField, self).to_representation(obj)

    def to_internal_value(self, data):
        if isinstance(data, dict):
            _model = data.pop('_model', None)
            _module = data.pop('_module', None)
            if _model is None or _module is None:
                return data
            else:
                return self._get_instance(_module, _model, data)
        else:
            return data

    @classmethod
    def _get_instance(cls, _module, _model, data):
        model = get_class('{}.{}'.format(_module, _model))
        obj_id = data.pop('id', None)

        if issubclass(model, BDocument):
            try:
                return model.objects.get(id=obj_id)
            except model.DoesNotExist:
                return None
        if issubclass(model, EmbeddedDocument):
            try:
                return model(**data)
            except model.DoesNotExist:
                return None

    def run_validators(self, *args):
        pass


class BSerializerField(serializers.Field):
    _serializer = None

    model = None
    _serializer = None
    _serializer_parent = None

    def __init__(self, *args, **kwargs):
        serializer = kwargs.pop('serializer', None)

        if serializer is not None:
            if isinstance(serializer, str):
                self._serializer = get_model_class(serializer)
            else:
                self._serializer = serializer
            self.model = self._serializer.Meta.model

        super(BSerializerField, self).__init__(**kwargs)

    def to_representation(self, obj):
        raise NotImplementedError(
            '{cls}.to_representation() must be implemented for field '
            '{field_name}. If you do not need to support write operations '
            'you probably want to subclass `ReadOnlyField` instead.'.format(
                cls=self.__class__.__name__,
                field_name=self.field_name,
            )
        )

    def to_internal_value(self, data):
        raise NotImplementedError(
            '{cls}.to_internal_value() must be implemented.'.format(
                cls=self.__class__.__name__
            )
        )

    def bind(self, field_name, parent):
        super(BSerializerField, self).bind(field_name, parent)
        self._top_level_context = self.context

    def get_serializer(self, *args, **kwargs):
        serializer = self._serializer(*args, **kwargs)
        setattr(serializer, "_top_level_context", self._top_level_context)

        return serializer


class BEmbeddedListField(BSerializerField):
    sorted_by = None

    def __init__(self, sorted_by=False, **kwargs):
        self.sorted_by = sorted_by
        super(BEmbeddedListField, self).__init__(**kwargs)

    def to_representation(self, obj):
        if obj is None:
            return []
        else:
            if self.sorted_by:
                _d = sorted(obj, key=attrgetter('order'))
                return self.get_serializer(_d, many=True).data
            else:
                return self.get_serializer(obj, many=True).data

    def to_internal_value(self, data):
        _d = []
        for value in data:
            serializer = self.get_serializer(data=value)
            serializer.is_valid(raise_exception=True)
            _d.append(serializer.validated_data)
        return _d


class BReferenceField(BSerializerField):
    def __init__(self, **kwargs):
        super(BReferenceField, self).__init__(**kwargs)
