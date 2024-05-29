from django.urls import path
from .views import *





urlpatterns = [
    
    #USER AUTHENTICATION
    path('create_user/', CreateUserView.as_view(), name='create_user'),
    path('login_user/', LoginUserView.as_view(), name='login_user'),
]