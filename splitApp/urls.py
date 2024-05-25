from django.urls import path
from .views import *

urlpatterns = [
    
    #USER AUTHENTICATION
    path('create_user/', create_user),
    path('login_user/', login_user),

    path("create_expense/", CreateExpense.as_view(), name="create_expense"),
    path('expenses/', ListExpenses.as_view(), name='list-expenses'),
    path('expenses/<int:pk>/', ListExpenses.as_view(), name='expense-details'),
    path('expenses/share/', ShareExpense.as_view(), name='share-expense'),
    path('wallet_balance/', CheckWalletBalance.as_view(), name = 'wallet_balance'),


    #ADMIN VIEWS
    path('admin/expenses/', AdminListExpenses.as_view(),name='admin-list-expenses'),
    path('admin/expenses/<int:pk>/', AdminListExpenses.as_view(),name='admin-detail-expense'),

]

