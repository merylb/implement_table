from rest_framework.fields import CharField, EmailField, ListField, BooleanField
from rest_framework_mongoengine.serializers import EmbeddedDocumentSerializer, DocumentSerializer

from implement_table.core.fields import BReferenceField
from implement_table.shared.contact.models import ContactInfo
from implement_table.shared.locations.serializer import CountrySerializer, CitySerializer, ProvinceSerializer


class ContactInfoSerializer(EmbeddedDocumentSerializer):
    address = CharField(required=False, allow_null=True, allow_blank=True)
    code_postal = CharField(required=False, allow_null=True, allow_blank=True)

    email = CharField(required=False, allow_null=True, allow_blank=True)

    phone_numbers = ListField(child=CharField(allow_blank=True), allow_null=True, required=False)
    country = BReferenceField(serializer=CountrySerializer, read_only=False, required=False, allow_null=True)
    city = BReferenceField(serializer=CitySerializer, read_only=False, required=False, allow_null=True)
    province = BReferenceField(serializer=ProvinceSerializer, read_only=False, required=False, allow_null=True)

    class Meta:
        model = ContactInfo
        fields = ("address", "code_postal", "email", "phone_numbers", "country", "city", "province")
