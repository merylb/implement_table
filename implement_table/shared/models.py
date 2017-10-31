from mongoengine.document import EmbeddedDocument
from mongoengine.fields import StringField, DynamicField, EmbeddedDocumentListField, BooleanField, DateTimeField, \
    FloatField, EmbeddedDocumentField
from implement_table.core.classes import BDocument


class AttachedFile(EmbeddedDocument):
    pass


class DocumentState(EmbeddedDocument):
    is_archived = BooleanField(default=False)
    archived_at = DateTimeField()
    is_closed = BooleanField(default=False)
    closed_at = DateTimeField()
    is_draft = BooleanField(default=True)
    is_valid = BooleanField(default=False)


class BillingDocument(BDocument):
    number = StringField(required=True)
    beneficiary = DynamicField()
    comment = StringField()
    doc_date = DateTimeField()
    attached_files = EmbeddedDocumentListField(AttachedFile)
    states = EmbeddedDocumentField(DocumentState)
    # owner=
    meta = {'abstract': True}


class Currency(BDocument):
    full_name = StringField()
    short_name = StringField()
    fraction_name = StringField()
    fraction_link_word = StringField()
    is_default = BooleanField(default=False)


class BillingList(BDocument):
    meta = {
        'abstract': True
    }


class Modality(BillingList):
    pass


class Bank(BillingList):
    pass


class PaymentModeType(BillingList):
    pass


class Tariff(EmbeddedDocument):
    tm = FloatField()
    tp = FloatField()
