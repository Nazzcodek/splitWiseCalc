from django.urls import path
from splitApp.views import *


urlpatterns = [
    path('create_user/', create_user),
    path('login_user/', login_user),
    path('create_expense/', create_expense),
]