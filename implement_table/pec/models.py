from mongoengine.document import EmbeddedDocument
from mongoengine.fields import StringField, FloatField, EmbeddedDocumentListField

from implement_table.shared.models import BillingDocument


class CareRequestAnswer(EmbeddedDocument):
    quotation = FloatField()
    description = StringField()
    ref = StringField()
    type = StringField()


class CareRequestLine(EmbeddedDocument):
    code = StringField()
    quotation = FloatField()
    qte = FloatField()


class CareRequest(BillingDocument):
    details = EmbeddedDocumentListField(CareRequestLine)
    answers = EmbeddedDocumentListField(CareRequestAnswer)
