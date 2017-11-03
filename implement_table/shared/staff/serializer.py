from rest_framework.fields import CharField, BooleanField, ListField, NullBooleanField
from rest_framework_mongoengine.serializers import DocumentSerializer

from implement_table.shared.staff.models import Service, MedicalSpeciality


class ServiceSerializer(DocumentSerializer):
    name = CharField(required=True)

    class Meta:
        model = Service
        fields = ('id', 'name')


class MedicalSpecialitySerializer(DocumentSerializer):
    long_title = CharField(required=True)
    short_title = CharField(required=True)

    is_surgical = NullBooleanField(required=False)
    is_internal = NullBooleanField(required=False)
    is_diagnostic = NullBooleanField(required=False)
    is_therapeutic = NullBooleanField(required=False)
    is_organ_based = NullBooleanField(required=False)
    is_technique_based = NullBooleanField(required=False)

    class Meta:
        model = MedicalSpeciality
        fields = ('id', 'long_title', 'short_title', 'is_surgical', 'is_internal', 'is_diagnostic', 'is_therapeutic',
                  'is_organ_based', 'is_technique_based')


class StaffMinimalSerializer(DocumentSerializer):
    full_name = CharField(read_only=True)
    contact_info = ContactInfoSerializer(many=False, read_only=False, allow_null=True, required=False)

    class Meta:
        model = Staff
        fields = ('id', 'full_name', 'contact_info')


class StaffSerializer(DocumentSerializer):
    first_name = CharField(required=True)
    last_name = CharField(required=True)
    full_name = CharField(read_only=True)
    birth_date = MnDateField(required=False)

    contact_info = ContactInfoSerializer(many=False, read_only=False, allow_null=True, required=False)

    user = MnReferenceField(serializer=MnUserSerializer, read_only=False, required=False, write_only=True)
    main_speciality = MnReferenceField(serializer=MedicalSpecialitySerializer, read_only=False)

    title = MnReferenceField(serializer='shared.lists.TitleSerializer')

    service = MnEditableReferenceField(serializer=ServiceSerializer, write_only=True)

    class Meta:
        model = Staff
        fields = (
            'id', 'title', 'first_name', 'last_name', 'birth_date', 'contact_info', 'main_speciality', 'user',
            'service', 'full_name')


class PhysicianSerializer(StaffSerializer):
    name_initials = CharField()
    is_licenced = BooleanField(required=False)
    reference_number = CharField(required=False)

    full_name = CharField(read_only=True)

    main_speciality = MnReferenceField(serializer=MedicalSpecialitySerializer, required=True, read_only=False)

    auxiliary_speciality = ListField(MnReferenceField(serializer=MedicalSpecialitySerializer))

    class Meta:
        model = Physician
        fields = (
            'id', 'title', 'first_name', 'last_name', 'name_initials', 'is_licenced', 'birth_date', 'contact_info',
            'reference_number', 'auxiliary_speciality', 'main_speciality', 'user', 'full_name', 'service'
        )


class PhysicianMinimalSerializer(DocumentSerializer):
    name_initials = CharField()
    is_licenced = BooleanField(required=False)
    reference_number = CharField(required=False)
    full_name = CharField(read_only=True)

    class Meta:
        model = Physician
        fields = ('id', 'name_initials', 'is_licenced', 'reference_number', 'full_name')


class PhysicianContactSerializer(DocumentSerializer):
    first_name = CharField(required=True)
    last_name = CharField(required=True)
    birth_date = MnDateField(required=False)

    contact_info = ContactInfoSerializer(many=False, read_only=False, allow_null=True, required=False)

    main_speciality = MnReferenceField(serializer=MedicalSpecialitySerializer, read_only=False, required=False)
    title = MnReferenceField(serializer=TitleSerializer, required=False, allow_null=True)

    name_initials = CharField(required=False, allow_blank=True, allow_null=True)
    is_licenced = BooleanField(required=False)
    reference_number = CharField(required=False)

    main_speciality = MnReferenceField(serializer=MedicalSpecialitySerializer, required=False, read_only=False)

    full_name = CharField(read_only=True)

    _module = CharField(read_only=True)
    _model = CharField(read_only=True)
    track_by = CharField(read_only=True)

    class Meta:
        model = PhysicianContact
        fields = (
            'id', 'title', 'first_name', 'last_name', 'name_initials', 'is_licenced', 'birth_date', 'contact_info',
            'reference_number', 'main_speciality', 'full_name', '_module', '_model', 'track_by'
        )


class PhysicianContactMinimalSerializer(DocumentSerializer):
    name_initials = CharField()
    is_licenced = BooleanField(required=False)
    reference_number = CharField(required=False)

    full_name = CharField(read_only=True)

    _module = CharField(read_only=True)
    _model = CharField(read_only=True)
    track_by = CharField(read_only=True)

    class Meta:
        model = PhysicianContact
        fields = (
            'id', 'name_initials', 'is_licenced', 'reference_number', 'full_name', '_module', '_model', 'track_by')
