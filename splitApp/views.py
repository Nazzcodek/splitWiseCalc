import jwt
from datetime import datetime, timedelta
from decimal import Decimal

from django.conf import settings as s
from django.contrib.auth import authenticate
from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework import status, mixins, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from splitApp.models import Expense, ExpenseSharing, User, UserWallet
from splitApp.services import *
from .services import calculate_expense_sharing_values
from .serializers import ExpenseSerializer, ExpenseSharingSerializer



# Create your views here.



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


class CreateExpense(mixins.CreateModelMixin, generics.GenericAPIView):
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data
        data['paid_by'] = request.user.id
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class ListExpenses(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk=None):
        user = request.user

        if pk is not None:
            try:
                expense = Expense.objects.get(id=pk, paid_by=user)
                serializer = ExpenseSerializer(expense)
                return Response(serializer.data)
            except Expense.DoesNotExist:
                raise ValueError("Expense does not exist")

        expenses = Expense.objects.filter(paid_by=user)
        serializer = ExpenseSerializer(expenses, many=True)
        return Response(serializer.data)


    def put(self, request, pk=None):
            user = request.user
            if pk is not None:
                try:
                    expense = Expense.objects.get(id=pk, paid_by=user)
                except Expense.DoesNotExist:
                    return Response({"error": "Expense does not exist"}, status=status.HTTP_404_NOT_FOUND)

                # Check if the expense has been shared
                if ExpenseSharing.objects.filter(expense=expense).exists():
                    return Response({"error": "Expense cannot be updated, it has already been shared"}, status=status.HTTP_400_BAD_REQUEST)

                data = request.data
                serializer = ExpenseSerializer(expense, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response({"error": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)




class ShareExpense(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        shared_expenses = ExpenseSharing.objects.filter(expense__paid_by = user)
        serializer = ExpenseSharingSerializer(shared_expenses, many=True)
        return Response (data=serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user
        data = request.data

        try:
            expense = Expense.objects.get(id=data['expense'], paid_by=user)

             # Check if the expense has already been shared
            if ExpenseSharing.objects.filter(expense=expense).exists():
                return ValueError('This expense has already been shared')

        except Expense.DoesNotExist:
            return Response({"error": "Expense does not exist"}, status=status.HTTP_404_NOT_FOUND)
        

        data['expense'] = expense.id  # Ensure expense is set correctly
        split_with_users = data.get('split_with', [])
        total_shares = len(split_with_users)

        if not split_with_users:
            return Response({"error": "split_with must be a non-empty list"}, status=status.HTTP_400_BAD_REQUEST)
        
        data['total_shares'] = total_shares  # Set total shares based on split_with length

        serializer = ExpenseSharingSerializer(data=data)
        if serializer.is_valid():
            method = serializer.validated_data['method']

            # Calculate shares
            values = request.data.get('values', []) if method in ["EXACT", "PERCENT"] else []
            try:
                shares = calculate_expense_sharing_values(method, expense.amount, values, total_shares)
            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():
                # Save the ExpenseSharing object
                expense_sharing = serializer.save()

                # Update total shares if it's null
                if expense_sharing.total_shares is None:
                    expense_sharing.total_shares = total_shares
                    expense_sharing.save()

                # Apply the expense sharing logic
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

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class CheckWalletBalance(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user.id  # Assuming request.user is a User object

        try:
            # Retrieve the user's wallet
            user_wallet = UserWallet.objects.get(owner__id=user)

            # Get the wallet balance
            wallet_balance = check_balance(user_wallet)
            

            return Response(data= wallet_balance, status=status.HTTP_200_OK)

        except UserWallet.DoesNotExist:
            # Handle case where user's wallet does not exist
            return Response({'error': 'User wallet not found'}, status=status.HTTP_404_NOT_FOUND)






# ADMIN VIEWS
class AdminListExpenses(APIView):
    serializer_class = ExpenseSerializer
    # permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get(self, request, pk=None):
        if pk is not None:
            user = get_object_or_404(User, pk=pk)
            expense = Expense.objects.filter(paid_by=user)
            serializer = self.serializer_class(expense, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            expenses = Expense.objects.all()
            serializer = self.serializer_class(expenses, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
