from django.urls import path
from .views import *


urlpatterns = [
    path('expenses/', ExpenseAPIView.as_view(), name='list-expenses'),
    path('expenses/<int:pk>/', ExpenseAPIView.as_view(), name='expense-details'),
    path('expenses/share/', ShareExpense.as_view(), name='share-expense'),
    path('wallet_balance/', CheckWalletBalance.as_view(), name = 'wallet_balance'),

    #ADMIN VIEWS
    path('admin/expenses/', AdminListExpenses.as_view(),name='admin-list-expenses'),
    path('admin/expenses/<int:pk>/', AdminListExpenses.as_view(),name='admin-detail-expense'),
    path('admin/user_wallets/', AdminViewUserWallets.as_view(), name = 'admin_user_wallets'),
    path('admin/user_wallets/<int:pk>/', AdminViewUserWallets.as_view(), name = 'admin_user_wallet_details')

]

