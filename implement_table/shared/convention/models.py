from mongoengine.fields import FloatField, EmbeddedDocumentField, EmbeddedDocumentListField, ReferenceField, StringField
from mongoengine.document import EmbeddedDocument

from implement_table.core.classes import BDocument
from implement_table.shared.models import Tariff
from implement_table.shared.procedure.models import Procedure


class ConventionException(EmbeddedDocument):
    procedure = ReferenceField(Procedure)
    tariff = EmbeddedDocumentField(Tariff)


class Convention(BDocument):
    label = StringField()
    tariff = EmbeddedDocumentField(Tariff)
    min = FloatField()
    max = FloatField()
    exceptions = EmbeddedDocumentListField(ConventionException)
