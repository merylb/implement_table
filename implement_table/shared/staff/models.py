from mongoengine import StringField, DateTimeField, EmbeddedDocumentField, ReferenceField, BooleanField, ListField

# from App.core.classes import MnDocument
# from App.authentication.models import MnUser
# from App.core.utils import FullName, ModuleModel
# from App.shared.lists.models import Title
# from App.shared.models import ContactInfo
from implement_table.authentication.models import MnUser
from implement_table.core.classes import BDocument
from implement_table.core.utils import FullName, ModuleModel
from implement_table.shared.contact.models import ContactInfo
from implement_table.shared.lists.models import Title


class Service(BDocument):
    name = StringField(required=True)


class MedicalSpeciality(BDocument):
    long_title = StringField(required=True)
    short_title = StringField(required=True)
    is_surgical = BooleanField(default=None)
    is_internal = BooleanField(default=None)
    is_diagnostic = BooleanField(default=None)
    is_therapeutic = BooleanField(default=None)
    is_organ_based = BooleanField(default=None)
    is_technique_based = BooleanField(default=None)
    super_speciality = ReferenceField('self')


class Staff(BDocument, FullName):
    title = ReferenceField(Title)
    last_name = StringField(required=True)
    first_name = StringField(required=True)
    birth_date = DateTimeField()
    contact_info = EmbeddedDocumentField(ContactInfo)
    user = ReferenceField(MnUser)
    main_speciality = ReferenceField(MedicalSpeciality)

    service = ReferenceField(Service)

    meta = {
        'allow_inheritance': True
    }


class Physician(Staff):
    name_initials = StringField(required=True)
    is_licenced = BooleanField()
    reference_number = StringField()
    main_speciality = ReferenceField(MedicalSpeciality, required=True)
    auxiliary_speciality = ListField(ReferenceField(MedicalSpeciality))


class PhysicianContact(BDocument, FullName, ModuleModel):
    title = ReferenceField(Title)
    last_name = StringField(required=True)
    first_name = StringField(required=True)
    birth_date = DateTimeField()
    contact_info = EmbeddedDocumentField(ContactInfo)

    name_initials = StringField()
    is_licenced = BooleanField()
    reference_number = StringField()
    main_speciality = ReferenceField(MedicalSpeciality)

    default_serializer = "PhysicianContactMinimalSerializer"
