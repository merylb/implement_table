from App.authentication.serializer import MnUserSerializer
from App.core.classes import MnEventSet
from App.core.mixins import UniqueFieldValidationMixin


class UserNameValidationEvents(MnEventSet, UniqueFieldValidationMixin):
    serializer_class = MnUserSerializer
    unique_field = "username"
