from mongoengine.document import EmbeddedDocument, Document
from mongoengine.fields import StringField, BooleanField, FloatField, ReferenceField, IntField, EmbeddedDocumentField, \
    ListField

from implement_table.core.classes import BDocument
from implement_table.shared.models import Modality


class NGAPCode(EmbeddedDocument):
    key = StringField()


class CCAMCode(EmbeddedDocument):
    key = StringField()


class Procedure(BDocument):
    name = StringField(required=True, unique=True)
    code = StringField(required=True, unique=True)
    price = FloatField(default=0)
    is_refundable = BooleanField()
    average_duration = IntField()
    length_of_hospitalization = IntField()
    NGAP_code = EmbeddedDocumentField(NGAPCode)
    CCAM_code = EmbeddedDocumentField(CCAMCode)
    modality = ReferenceField(Modality)
    tnr = FloatField(default=0)


class ProcedureCatalog(BDocument):
    name = StringField(required=True, unique=True)
    is_default = BooleanField()
    procedures = ListField(ReferenceField(Procedure))
