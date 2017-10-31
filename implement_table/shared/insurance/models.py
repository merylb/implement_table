from mongoengine.fields import FloatField, EmbeddedDocumentListField, ReferenceField, StringField, BooleanField, \
    EmailField, ListField
from mongoengine.document import EmbeddedDocument

from implement_table.core.classes import BDocument
from implement_table.shared.convention.models import Convention


class OrganizationConvention(EmbeddedDocument):
    is_default = BooleanField(default=True)
    convention = ReferenceField(Convention)


class Organization(BDocument):
    name = StringField()
    contact_full_name = StringField()
    default_refund_amount = FloatField(default=0)
    conventions = EmbeddedDocumentListField(OrganizationConvention)
    address = StringField()
    email = EmailField()
    phone_numbers = ListField(field=StringField(), required=False, default=[])
