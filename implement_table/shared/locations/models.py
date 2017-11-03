from mongoengine import ReferenceField, StringField

from implement_table.core.classes import BDocument



class Location(BDocument):
    short_name = StringField()
    full_name = StringField(required=True, unique=True)

    meta = {
        'abstract': True
    }


class Country(Location):
    pass


class City(Location):
    country = ReferenceField(Country)

    @property
    def country_id(self):
        return getattr(self.country, 'id', None)

    meta = {
        'indexes': [
            'country'
        ]
    }


class Province(Location):
    city = ReferenceField(City)

    @property
    def city_id(self):
        return getattr(self.city, 'id', None)

    meta = {
        'indexes': [
            'city'
        ]
    }
