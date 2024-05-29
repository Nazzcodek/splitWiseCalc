from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework import status, mixins, generics, permissions
from rest_framework.response import Response

from splitApp.models import Expense, ExpenseSharing, UserWallet
from services.expense_services import *
from services.response_services import *
from .serializers import ExpenseSerializer, ExpenseSharingSerializer,UserWalletSerializer


# Imports for Swagger
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from django.contrib.auth import get_user_model

User = get_user_model()







# Create your views here.



class ExpenseAPIView(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    generics.GenericAPIView
):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]


    
    @swagger_auto_schema(
        operation_description="Create a new expense",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['title', 'description', 'amount'],
            properties={
                'title': openapi.Schema(type=openapi.TYPE_STRING, description='Title of the expense'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='Description of the expense'),
                'amount': openapi.Schema(type=openapi.TYPE_NUMBER, format='float', description='Amount of the expense')
            },
        ),
        responses={
            201: openapi.Response(
                description="Expense created successfully",
                examples={
                    "application/json": {
                        "transaction_id": "UUID",
                        "paid_by": "user_id",
                        "title": "Expense Title",
                        "description": "Expense Description",
                        "amount": 100.00,
                        "created_at": "timestamp",
                        "updated_at": "timestamp"
                    }
                }
            ),
            400: openapi.Response(
                description="Bad Request",
                examples={
                    "application/json": {
                        "error": "Detailed error message"
                    }
                }
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        try:
            data  = request.data
            data['paid_by'] = request.user.id
            serializer = ExpenseSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return create_success_response(data=serializer.data)
            return create_error_response(serializer.errors)
        except Exception as e:
            return create_error_response(str(e))

    @swagger_auto_schema(
        operation_description="Retrieve a list of expenses",
        responses={
            200: openapi.Response(
                description="List of expenses",
                examples={
                    "application/json": [
                        {
                            "transaction_id": "UUID",
                            "paid_by": "user_id",
                            "title": "Expense Title",
                            "description": "Expense Description",
                            "amount": 100.00,
                            "created_at": "timestamp",
                            "updated_at": "timestamp"
                        }
                    ]
                }
            ),
        },
    )
    def get(self, request, *args, **kwargs):
        try:
            pk = kwargs.get('pk')
            if pk is not None:
                return self.retrieve(request, *args, **kwargs)  # Retrieve a specific object
            else:
                return self.list(request, *args, **kwargs)  # List all objects
        except Exception as e:
            return create_error_response(str(e))

    @swagger_auto_schema(
        operation_description="Update an existing expense",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'title': openapi.Schema(type=openapi.TYPE_STRING, description='Title of the expense'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='Description of the expense'),
                'amount': openapi.Schema(type=openapi.TYPE_NUMBER, format='float', description='Amount of the expense')
            },
        ),
        responses={
            200: openapi.Response(
                description="Expense updated successfully",
                examples={
                    "application/json": {
                        "transaction_id": "UUID",
                        "paid_by": "user_id",
                        "title": "Expense Title",
                        "description": "Expense Description",
                        "amount": 100.00,
                        "created_at": "timestamp",
                        "updated_at": "timestamp"
                    }
                }
            ),
            400: openapi.Response(
                description="Bad Request",
                examples={
                    "application/json": {
                        "error": "Expense cannot be updated, it has already been shared"
                    }
                }
            ),
            404: openapi.Response(
                description="Expense not found",
                examples={
                    "application/json": {
                        "error": "Expense does not exist"
                    }
                }
            ),
            405: openapi.Response(
                description="Method not allowed",
                examples={
                    "application/json": {
                        "error": "Method not allowed"
                    }
                }
            ),
        },
    )
    def put(self, request, *args, **kwargs):
        try:
            expense_id = kwargs.get('pk')
            expense = Expense.objects.get(pk=expense_id, paid_by=request.user)
            data = request.data
            data['paid_by'] = request.user.id
            serializer = ExpenseSerializer(expense, data=data, partial=False)
            if serializer.is_valid():
                serializer.save()
                return create_success_response(data=serializer.data)
            return create_error_response(serializer.errors)
        except Expense.DoesNotExist:
            return not_found_response(error_message='Not found')
        except Exception as e:
            return create_error_response(str(e))



class ShareExpense(    
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]


    @swagger_auto_schema(
        operation_description="Retrieve all shared expenses for the authenticated user",
        responses={
            200: openapi.Response(
                description="List of shared expenses",
                examples={
                    "application/json": [
                        {
                            "id": "UUID",
                            "expense": "expense_id",
                            "method": "EQUAL",
                            "split_with": ["user1", "user2"],
                            "values": [],
                            "total_shares": 2,
                            "created_at": "timestamp",
                            "updated_at": "timestamp"
                        }
                    ]
                }
            ),
        },
    )
    def get(self, request):
        try:
            user = request.user
            shared_expenses = ExpenseSharing.objects.filter(expense__paid_by = user)
            serializer = ExpenseSharingSerializer(shared_expenses, many=True)
            return get_success_response(data=serializer.data)
        except Exception as e:
            return create_error_response(str(e))


    @swagger_auto_schema(
        operation_description="Share an expense with other users",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'expense': openapi.Schema(type=openapi.TYPE_STRING, description='ID of the expense to be shared'),
                'method': openapi.Schema(type=openapi.TYPE_STRING, description='Method of sharing (EQUAL, EXACT, PERCENT)'),
                'split_with': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING), description='List of user IDs to split the expense with'),
                'values': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_NUMBER), description='Values for EXACT or PERCENT method'),
            },
            required=['expense', 'method', 'split_with']
        ),
        responses={
            201: openapi.Response(
                description="Expense shared successfully",
                examples={
                    "application/json": {
                        "transaction_id": "UUID",
                        "paid_by": "username",
                        "title": "Expense Title",
                        "description": "Expense Description",
                        "amount": 100.00,
                        "split_with": ["user1", "user2"],
                        "shares": [50.00, 50.00]
                    }
                }
            ),
            400: openapi.Response(
                description="Bad Request",
                examples={
                    "application/json": {
                        "error": "split_with must be a non-empty list"
                    }
                }
            ),
            404: openapi.Response(
                description="Expense not found",
                examples={
                    "application/json": {
                        "error": "Expense does not exist"
                    }
                }
            ),
        },
    )
    def post(self, request):
            try:
                user = request.user
                data = request.data

                try:
                    expense = Expense.objects.get(id=data['expense'], paid_by=user)

                    # Check if the expense has already been shared
                    if ExpenseSharing.objects.filter(expense=expense).exists():
                        return create_error_response('This expense has already been shared')

                except Expense.DoesNotExist:
                    return not_found_response(error_message='Not found')

                split_with_users = data.get('split_with', [])
                total_shares = len(split_with_users)

                if not split_with_users:
                    return create_error_response('No users to split with')
                
                data['expense'] = expense.id  # Ensure expense is set correctly
                data['total_shares'] = total_shares  # Set total shares based on split_with length

                serializer = ExpenseSharingSerializer(data=data)
                if serializer.is_valid():
                    method = serializer.validated_data['method']

                    # Calculate shares
                    values = request.data.get('values', []) if method in ["EXACT", "PERCENT"] else []
                    try:
                        shares = calculate_expense_sharing_values(method, expense.amount, values, total_shares)
                    except ValueError as e:
                        return create_error_response( str(e))

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
                            'shares': shares,
                            'created_at': expense_sharing.created_at,
                            'updated_at': expense_sharing.updated_at
                        }

                    return create_success_response(data=expense_data)

                return create_error_response(serializer.errors)

            except Exception as e:
                return create_error_response( str(e))




class CheckWalletBalance(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve the balance of the authenticated user's wallet",
        responses={
            200: openapi.Response(
                description="User's wallet balance",
                examples={
                    "application/json": {
                        "balances": [
                            {"currency": "USD", "balance": 100.00},
                            {"currency": "EUR", "balance": 50.00}
                        ]
                    }
                }
            ),
            404: openapi.Response(
                description="User wallet not found",
                examples={
                    "application/json": {
                        "error": "User wallet not found"
                    }
                }
            )
        },
    )
    def get(self, request):

        try:
            user = request.user  # Assuming request.user is a User object
            # Retrieve the user's wallet
            user_wallet = UserWallet.objects.get(owner=user)

            # Get the wallet balance
            wallet_balance = check_balance(user_wallet)
            serializer = UserWalletSerializer(wallet_balance, many= True)
            
            return get_success_response(data=serializer.data)
        
        except UserWallet.DoesNotExist as e:
            return create_error_response(str(e))







# ADMIN VIEWS
class AdminListExpenses(generics.ListAPIView):
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]



    @swagger_auto_schema(
        operation_description="List all expenses for the authenticated admin user",
        responses={
            200: openapi.Response(
                description="List of expenses",
                examples={
                    "application/json": [
                        {
                            "transaction_id": "12345678-1234-5678-1234-567812345678",
                            "paid_by": "admin",
                            "title": "Expense 1",
                            "description": "Description of Expense 1",
                            "amount": 100.00
                        },
                        {
                            "transaction_id": "87654321-1234-5678-1234-567812345678",
                            "paid_by": "admin",
                            "title": "Expense 2",
                            "description": "Description of Expense 2",
                            "amount": 200.00
                        }
                    ]
                }
            )
        },
    )
    def get(self, request, pk=None):
        try:
            if not request.user.is_staff:  # Check if the user is not an admin
                return forbidden_response('You do not have permission to perform this action.')
            
            if pk is not None:
                user = get_object_or_404(User, pk=pk)
                expense = Expense.objects.filter(paid_by=user)
                serializer = self.serializer_class(expense, many=True)
                return get_success_response(data=serializer.data)
            else:
                expenses = Expense.objects.all()
                serializer = self.serializer_class(expenses, many=True)
                return get_success_response(data=serializer.data)
        except Exception as e:
            return create_error_response(str(e))

class AdminViewUserWallets(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    serializer_class = UserWalletSerializer



    @swagger_auto_schema(
        operation_description="List all user wallets for the authenticated admin user",
        responses={
            200: openapi.Response(
                description="List of user wallets",
                examples={
                    "application/json": [
                        {
                            "owner": "user1",
                            "balances": {
                                "USD": 100.0,
                                "EUR": 50.0
                            }
                        },
                        {
                            "owner": "user2",
                            "balances": {
                                "USD": 150.0,
                                "EUR": 75.0
                            }
                        }
                    ]
                }
            )
        },
    )
    def get(self, request, pk=None, *args, **kwargs):
        try:
            if not request.user.is_staff:  # Check if the user is not an admin
                return forbidden_response('You do not have permission to perform this action.')
        
            if pk is not None:
                # Retrieve the user's wallet
                user_wallet = UserWallet.objects.get(owner=pk)

                # Get the wallet balance
                wallet_balance = check_balance(user_wallet)
                serializer = UserWalletSerializer(wallet_balance, many=True)
                return get_success_response(data=serializer.data)
           # Retrieve all user wallets
            user_wallets = UserWallet.objects.all()
            serialized_wallets = []
            for wallet in user_wallets:
                # Get the wallet balance
                wallet_balance = check_balance(wallet)

                # Serialize the wallet balance
                serializer = UserWalletSerializer(data=wallet_balance, many=True)
                if serializer.is_valid():
                    serialized_wallets.append(serializer.data)
                else:
                    return create_error_response(serializer.errors) 
            return get_success_response(data = serialized_wallets)

        except Exception as e:
            return Response({'error': str(e)})