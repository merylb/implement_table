from rest_framework.fields import ChoiceField, CharField, IntegerField, NullBooleanField
from rest_framework_mongoengine.serializers import DocumentSerializer

from implement_table.shared.lists.models import Title, List, Profession, MaritalStatus, Ethnicity, Unit, BloodGroup, Bank, \
    PaymentModeType, PrescriptionFrequency, ExamIndication, Tva, StockUnit, PresentationForm, Modality


LIST_FIELDS = ('id', 'value', 'description', 'order', 'is_hidden')


class ListSerializer(DocumentSerializer):
    value = CharField()
    description = CharField(required=False, allow_null=True)
    order = IntegerField(required=False, allow_null=True)
    is_hidden = NullBooleanField(required=False)

    class Meta:
        model = List
        fields = LIST_FIELDS


class TitleSerializer(ListSerializer):
    gender = ChoiceField(choices=['MALE', 'FEMALE', 'UNDEFINED'], required=False, allow_null=True)

    class Meta:
        model = Title
        fields = LIST_FIELDS + ('gender',)


class ProfessionSerializer(ListSerializer):
    class Meta:
        model = Profession
        fields = LIST_FIELDS


class MaritalStatusSerializer(ListSerializer):
    class Meta:
        model = MaritalStatus
        fields = LIST_FIELDS


class EthnicitySerializer(ListSerializer):
    class Meta:
        model = Ethnicity
        fields = LIST_FIELDS


class UnitSerializer(ListSerializer):
    class Meta:
        model = Unit
        fields = LIST_FIELDS


class StockUnitSerializer(ListSerializer):
    class Meta:
        model = StockUnit
        fields = LIST_FIELDS


class BloodGroupSerializer(ListSerializer):
    class Meta:
        model = BloodGroup
        fields = LIST_FIELDS

class BankSerializer(ListSerializer):
    class Meta:
        model = Bank
        fields = LIST_FIELDS


class PaymentModeTypeSerializer(ListSerializer):
    class Meta:
        model = PaymentModeType
        fields = LIST_FIELDS


class PrescriptionFrequencySerializer(ListSerializer):
    class Meta:
        model = PrescriptionFrequency
        fields = LIST_FIELDS


class ExamIndicationSerializer(ListSerializer):
    class Meta:
        model = ExamIndication
        fields = LIST_FIELDS


class TvaSerializer(ListSerializer):
    class Meta:
        model = Tva
        fields = LIST_FIELDS


class ModalitySerializer(ListSerializer):
    class Meta:
        model = Modality
        fields = LIST_FIELDS
