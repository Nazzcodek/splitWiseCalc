from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        if request.path == '/api/login_user/':
            return None

        token = self.get_token_from_request(request)
        if token is None:
            return None

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user = User.objects.get(user_id=payload['user_id'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token expired')
        except jwt.DecodeError:
            raise AuthenticationFailed('Token is invalid')
        except User.DoesNotExist:
            raise AuthenticationFailed('No such user')

        return (user, token)

    def get_token_from_request(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '').split()
        if len(auth_header) == 2 and auth_header[0].lower() == 'bearer':
            return auth_header[1]
        return request.COOKIES.get('access_token')

    def authenticate_header(self, request):
        return 'Bearer'
