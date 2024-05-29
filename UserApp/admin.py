from django.contrib import admin
from .models import User

# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'username', 'email', 'is_staff', 'is_superuser', 'created_at', 'updated_at')
    search_fields = ('username', 'email')
    readonly_fields = ('user_id', 'created_at', 'updated_at')


admin.site.register(User, UserAdmin)