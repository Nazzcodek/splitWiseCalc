from django.urls import path
from .views import *


from . import views



urlpatterns = [
    
    #USER AUTHENTICATION
    path('create_user/', CreateUserView.as_view(), name='create_user'),
    path('seewallet/', seewallet, name='seewallet'),    
    path('login_user/', login_user, name='login_user'),

    path("create_expense/", CreateExpense.as_view(), name="create_expense"),
    path('expenses/', ListExpenses.as_view(), name='list-expenses'),
    path('expenses/<int:pk>/', ListExpenses.as_view(), name='expense-details'),
    path('expenses/share/', ShareExpense.as_view(), name='share-expense'),
    path('wallet_balance/', CheckWalletBalance.as_view(), name = 'wallet_balance'),


    #ADMIN VIEWS
    path('admin/expenses/', AdminListExpenses.as_view(),name='admin-list-expenses'),
    path('admin/expenses/<int:pk>/', AdminListExpenses.as_view(),name='admin-detail-expense'),
    path('admin/user_wallets/', AdminViewUserWallets.as_view(), name = 'admin_user_wallets'),
    path('admin/user_wallets/<int:pk>/', AdminViewUserWallets.as_view(), name = 'admin_user_wallet_details')

]

