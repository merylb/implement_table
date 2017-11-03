from rest_framework.fields import CharField, IntegerField
from rest_framework_mongoengine.serializers import DocumentSerializer

from implement_table.core.fields import BReferenceField
from implement_table.shared.locations.models import City, Province, Country


class CountrySerializer(DocumentSerializer):
    full_name = CharField(required=True)
    short_name = CharField(required=False)

    class Meta:
        model = Country
        fields = ('id', 'full_name', 'short_name')


class CitySerializer(DocumentSerializer):
    full_name = CharField(required=True)
    short_name = CharField(required=False)
    country = BReferenceField(serializer=CountrySerializer, write_only=True)

    country_id = IntegerField(read_only=True)

    class Meta:
        model = City
        fields = ('id', 'full_name', 'short_name', 'country', 'country_id')


class ProvinceSerializer(DocumentSerializer):
    full_name = CharField(required=True)
    short_name = CharField(required=False)
    city = BReferenceField(serializer=CitySerializer, write_only=True)

    city_id = IntegerField(read_only=True)

    class Meta:
        model = Province
        fields = ('id', 'full_name', 'short_name', 'city', 'city_id')
