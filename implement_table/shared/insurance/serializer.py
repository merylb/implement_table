from rest_framework.fields import BooleanField, CharField, FloatField, EmailField, ListField
from rest_framework_mongoengine.serializers import EmbeddedDocumentSerializer, DocumentSerializer

from implement_table.core.fields import BReferenceField, BEmbeddedListField
from implement_table.shared.convention.serializer import ConventionSerializer
from implement_table.shared.insurance.models import OrganizationConvention, Organization


class OrganizationConventionSerializer(EmbeddedDocumentSerializer):
    is_default = BooleanField(default=False)
    convention = BReferenceField(serializer=ConventionSerializer)

    class Meta:
        model = OrganizationConvention
        fields = ("is_default", "convention")


class OrganizationSerializer(DocumentSerializer):
    name = CharField(required=False, read_only=False, allow_null=True)
    contact_full_name = CharField(required=False, read_only=False, allow_null=True)
    default_refund_amount = FloatField(required=False, allow_null=True)
    conventions = BEmbeddedListField(serializer=OrganizationConventionSerializer, required=False, allow_null=True)

    address = CharField(required=False, read_only=False, allow_null=True)
    email = EmailField(required=False, allow_null=True)
    phone_numbers = ListField(child=CharField(), required=False, default=[])

    class Meta:
        model = Organization
        fields = ["id", "name", "contact_full_name", "default_refund_amount", "conventions", "address", "email",
                  "phone_numbers"]
