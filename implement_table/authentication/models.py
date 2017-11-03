from django.contrib.auth.hashers import make_password, check_password
from mongoengine import EmbeddedDocument, StringField, BooleanField, EmbeddedDocumentField, MapField, \
    ReferenceField, DateTimeField
from mongoengine.fields import SequenceField

from implement_table.core.classes import BDocument


class Resource(EmbeddedDocument):
    name = StringField(required=True)
    is_all = BooleanField(default=False)
    actions = MapField(StringField())


class Profile(BDocument):
    id = SequenceField(primary_key=True)
    name = StringField(required=True, unique=True)
    is_root = BooleanField(default=False)

    default_state = StringField()
    permissions = MapField(EmbeddedDocumentField(Resource))

    def is_allowed(self, resource, action):
        if not self.is_root:
            if resource in self.permissions and not self.permissions[resource].is_all:
                return action in self.permissions[resource].actions
            else:
                return resource in self.permissions
        else:
            return True


class MnUser(BDocument):
    id = SequenceField(primary_key=True)
    username = StringField(required=True)
    password = StringField(required=True)

    email = StringField(default=None)
    last_login_at = DateTimeField(default=None)
    is_active = BooleanField(default=True)
    is_special = BooleanField(default=False)
    profile = ReferenceField(Profile)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ()

    meta = {
        "collection": "user",
        'indexes': [
            {'fields': ['username'], 'unique': True, 'sparse': True}
        ]
    }

    def __unicode__(self):
        return self.username

    @staticmethod
    def is_anonymous():
        return False

    @staticmethod
    def is_authenticated():
        return True

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        return self.save()

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    @classmethod
    def create_user(cls, username, password):
        user = cls(username=username)
        return user.set_password(password)
