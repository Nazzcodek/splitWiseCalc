import jwt
from datetime import datetime, timedelta

from django.conf import settings as s
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.permissions import  AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from services.response_services import *
from .serializers import UserSerializer

# Imports for Swagger
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi



from django.contrib.auth import get_user_model

User = get_user_model()







# Create your views here.





class CreateUserView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @swagger_auto_schema(
        operation_description="Create a new user",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'email', 'password'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username for the new user'),
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email for the new user'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password for the new user'),
            },
        ),
        responses={
            201: openapi.Response(
                description="User created successfully",
                examples={
                    "application/json": {
                        "user_id": "UUID of the created user",
                        "username": "Username of the created user",
                        "email": "Email of the created user"
                    }
                }
            ),
            400: openapi.Response(
                description="Bad request",
                examples={
                    "application/json": {
                        "error": "All fields (username, email, password) are required."
                    }
                }
            ),
            500: openapi.Response(
                description="Internal server error",
                examples={
                    "application/json": {
                        "error": "An error occurred: {error_message}"
                    }
                }
            ),
        },
    )

    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')

        if not username or not email or not password:
            return Response({'error': 'All fields (username, email, password) are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.create_user(username=username, email=email, password=password)

            # Return user data as JSON
            user_data = {
                'user_id': user.user_id,  # Assuming 'user_id' is the field used for UUID
                'username': user.username,
                'email': user.email
            }
            return Response(user_data, status=status.HTTP_201_CREATED) 

        except Exception as e:
            return Response({'error': f'An error occurred: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class LoginUserView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = UserSerializer

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'password'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='User\'s username'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='User\'s password')
            }
        ),
        responses={
            200: openapi.Response(
                description='Successful login',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'token': openapi.Schema(type=openapi.TYPE_STRING, description='Authentication token')
                    }
                )
            ),
            400: openapi.Response(description='Invalid input / Error in authentication')
        },
        security=[]
    )
    @csrf_exempt
    def post(self, request):
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                username = serializer.validated_data.get("username")
                password = serializer.validated_data.get("password")
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    user_id = str(user.user_id)
                    payload = {
                        'user_id': user_id,
                        'exp': datetime.utcnow() + timedelta(minutes=60),
                        'iat': datetime.utcnow()
                    }
                    token = jwt.encode(payload, s.SECRET_KEY, algorithm='HS256')
                    response = create_success_response({'token': token})
                    response.set_cookie(key='access_token', value=token, httponly=True)
                    return response
                else:
                    return create_error_response("Invalid credentials")
            else:
                return create_error_response(serializer.errors)




