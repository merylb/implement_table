from mongoengine.document import EmbeddedDocument
from mongoengine.fields import StringField, EmailField, ListField, ReferenceField

from implement_table.shared.locations.models import Country, City, Province


class ContactInfo(EmbeddedDocument):
    address = StringField()
    code_postal = StringField()
    email = EmailField()
    phone_numbers = ListField(field=StringField(), required=False, default=[])
    country = ReferenceField(Country)
    city = ReferenceField(City)
    province = ReferenceField(Province)

