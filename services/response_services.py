from rest_framework import status
from rest_framework.response import Response


def get_success_response(data=None):
    return Response(data, status=status.HTTP_200_OK)

def create_success_response(data=None):
    return Response(data, status=status.HTTP_201_CREATED)

def create_error_response(error_message, status_code=status.HTTP_400_BAD_REQUEST):
    return Response({'error': error_message}, status=status_code)

def not_found_response(error_message='Not found'):
    return Response({'error': error_message}, status=status.HTTP_404_NOT_FOUND)

def forbidden_response(error_message='Forbidden'):
    return Response({'error': error_message}, status=status.HTTP_403_FORBIDDEN)

def unauthorized_response(error_message='Unauthorized'):
    return Response({'error': error_message}, status=status.HTTP_401_UNAUTHORIZED)
