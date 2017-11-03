from mongoengine import StringField, IntField
from mongoengine.fields import BooleanField, ReferenceField, EmbeddedDocumentField

from implement_table.core.classes import BDocument


class List(BDocument):
    value = StringField(required=True)
    description = StringField()
    order = IntField()
    is_hidden = BooleanField(default=False)

    meta = {
        'allow_inheritance': True
    }


class Title(List):
    gender = StringField(default="UNDEFINED")


class Profession(List):
    pass


class MaritalStatus(List):
    pass


class Ethnicity(List):
    pass


class Unit(List):
    pass


class StockUnit(List):
    pass


class BloodGroup(List):
    pass


class Bank(List):
    pass


class PaymentModeType(List):
    pass


# prescription
class PrescriptionFrequency(List):
    pass


# exam
class ExamIndication(List):
    pass


class Tva(List):
    pass


# medicine
class INN(List):
    pass


class TherapeuticClass(List):
    pass


class Laboratory(List):
    pass


class MedicineCategory(List):
    pass


class DosageForm(List):
    plural_value = StringField()


class PresentationForm(List):
    dosage_form = ReferenceField(DosageForm)


class Modality(List):
    pass
