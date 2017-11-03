from rest_framework_jwt.authentication import BaseJSONWebTokenAuthentication


class MnAuthenticationUrl(BaseJSONWebTokenAuthentication):
    def get_jwt_value(self, request):
        return request.query_params.get('auth')
