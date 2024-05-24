from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from splitApp.services import *
from datetime import datetime, timedelta
import jwt
from splitApp.models import Expense, ExpenseSharing, User
from decimal import Decimal
from django.db import transaction
from django.conf import settings as s


@api_view(['POST'])
def create_user(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')

    if not username or not email or not password:
        return Response({'error': 'All fields (username, email, password) are required.'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            assign_create_expense_permission(user)

            # Return user data as JSON
            user_data = {
                'id': user.id, 
                'username': user.username,
                'email': user.email
            }
            return Response(user_data, status=status.HTTP_201_CREATED) 

        except Exception as e:
            return Response({'error': f'An error occurred: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(request, username=username, password=password)
    if user is not None:
        user_id = str(user.user_id)
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(minutes=60),
            'iat': datetime.utcnow()
        }

        token = jwt.encode(payload, s.SECRET_KEY, algorithm='HS256')

        # Set the token in an HttpOnly cookie
        response = Response({'token': token}, status=status.HTTP_200_OK)
        response.set_cookie(key='access_token', value=token, httponly=True)
        return response
    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_expense(request):
    if request.method == "POST":
        title = request.data.get('title')
        description = request.data.get('description')
        amount = Decimal(request.data.get('amount'))
        method = request.data.get('method')

        # Get split_with usernames
        split_with_usernames = request.data.get('split_with', [])
        if not isinstance(split_with_usernames, list):
            return Response({'error': 'split_with must be a list of usernames'}, status=status.HTTP_400_BAD_REQUEST)

        # Get User objects based on usernames
        split_with_users = []
        for username in split_with_usernames:
            try:
                split_with_users.append(User.objects.get(username=username))
            except User.DoesNotExist:
                return Response({'error': f'Invalid username: {username}'}, status=status.HTTP_400_BAD_REQUEST)

        values = request.data.get('values', []) if method in ["EXACT", "PERCENT"] else []
        total_shares = len(split_with_users)  # Only consider users in split_with

        try:
            shares = calculate_expense_sharing_values(method, amount, values, total_shares)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            expense = Expense.objects.create(
                paid_by=request.user,
                title=title,
                description=description,
                amount=amount
            )
            expense_sharing = ExpenseSharing.objects.create(
                expense=expense,
                method=method,
                total_shares=total_shares
            )
            expense_sharing.split_with.set(split_with_users)

            apply_expense(expense_sharing, shares)

            expense_data = {
                'transaction_id': expense.transaction_id,
                'paid_by': expense.paid_by.username,
                'title': expense.title,
                'description': expense.description,
                'amount': expense.amount,
                'split_with': [user.username for user in expense_sharing.split_with.all()],
                'shares': shares
            }

            return Response(expense_data, status=status.HTTP_201_CREATED)

    # If not POST, return an error
    return Response({'error': 'Invalid request method.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
