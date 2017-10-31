from mongoengine.fields import StringField, DynamicField
from mongoengine import queryset_manager

from implement_table.core.classes import BDocument


class AbstractConfig(BDocument):
    key = StringField(required=True)
    value = DynamicField()

    meta = {
        'abstract': True,
        'indexes': [
            'key',
        ]
    }

    @queryset_manager
    def _get_by_key_only(self, queryset, key, create=False):
        try:
            return queryset.get(key=key)
        except self.DoesNotExist:
            if create:
                return self(key=key)
            else:
                return None

    @queryset_manager
    def get_by_key_and_owner(self, queryset, key, owner):
        return queryset.get(key=key)

    @queryset_manager
    def _get_by_key_and_speciality(self, queryset, key, owner):
        return queryset.get(key=key)

    @classmethod
    def get_by_key(cls, key, owner=None, create=False):
        if owner is None:
            return cls._get_by_key_only(key, create=create)
        else:
            try:
                return cls.get_by_key_and_owner(key, owner)
            except cls.DoesNotExist:
                try:
                    return cls._get_by_key_and_speciality(key, owner)
                except cls.DoesNotExist:
                    return cls._get_by_key_only(key, create=create)


class BillingConfig(AbstractConfig):
    pass
