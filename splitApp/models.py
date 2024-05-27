from django.db import models
from uuid import uuid4
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser


class UserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

         # Ensure is_superuser and is_staff are True for superuser
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

         # Create a new superuser
        return self.create_user(username, email, password, **extra_fields)
    
        
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(AbstractUser, BaseModel):
    user_id = models.UUIDField(default=uuid4, editable=False)
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'password']

    objects = UserManager()

    def __str__(self):
        return self.username


class Expense(BaseModel):
    transaction_id = models.UUIDField(default=uuid4, editable=False)
    paid_by = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.paid_by} - {self.title} - {self.amount}"
    
    class Meta:
        permissions = [
            ("can_create_expense", "Can create expense"),
        ]


class UserWallet(BaseModel):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    # removed the is_owed and owed field from the model and refractor to balances
    balances = models.JSONField(default=dict)
   

class ExpenseSharing(BaseModel):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE)
    method = models.CharField(max_length=10, choices=[
        ('EQUAL', 'Equal'),
        ('EXACT', 'Exact'),
        ('PERCENT', 'Percent')
    ])
    split_with = models.ManyToManyField(User, blank=True)

    values = models.JSONField(default=list, null=True, blank=True)
    # Added total shares field
    total_shares = models.PositiveIntegerField(null=True)
