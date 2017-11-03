from datetime import datetime

# from App.authentication.serializer import MnUserSerializer, ProfileSerializer
# from App.core.classes import MnViewSet
# from App.shared.staff.models import Staff
# from App.shared.staff.serializer import StaffMinimalSerializer
from implement_table.authentication.serializer import MnUserSerializer, ProfileSerializer
from implement_table.core.classes import BViewSet
from implement_table.shared.staff.models import Staff
from implement_table.shared.staff.serializer import StaffMinimalSerializer


def jwt_response_payload_handler(token, user=None, request=None):
    user.last_login_at = datetime.now()
    user.save()

    try:
        staff = StaffMinimalSerializer(Staff.objects.get(user=user)).data
    except Staff.DoesNotExist:
        staff = False

    return {
        'token': token,
        'user': {
            'user': MnUserSerializer(user).data,
            'staff': staff
        }
    }


class ProfileViewSet(BViewSet):
    serializer_class = ProfileSerializer


class UserViewSet(BViewSet):
    serializer_class = MnUserSerializer
    resource = "user"
