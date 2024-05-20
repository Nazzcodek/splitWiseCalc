from django.db import models
from uuid import uuid4
from services import *


class BaseModel(models.Model):
    """This is the base model for fields associated with all models"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class User(BaseModel):
    user_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username


class Expense(BaseModel):
    transaction_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    paid_by = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.title} - {self.amount}"


class UserWallet(BaseModel):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    owes = models.JSONField(default=dict)
    is_owed = models.JSONField(default=dict)

    def add_owed(self, user_id, amount):
        add_owed(self, user_id, amount)

    def add_is_owed(self, user_id, amount):
        add_is_owed(self, user_id, amount)

    def check_balance(self):
        return check_balance(self, self.__class__)

    def __str__(self):
        return self.check_balance()


class ExpenseSharing(models.Model):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE)
    method = models.CharField(max_length=10)
    split_with = models.ManyToManyField(User, blank=True)
    values = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # If instance is new (i.e., it doesn't have a primary key yet), save without running the logic
        if not self.pk:
            super().save(*args, **kwargs)
            return

        # Calculate the values for expense sharing
        if calculate_expense_sharing_values(self):
            self.apply_expense()

        # Save again to update any changes
        super().save(*args, **kwargs)

    def apply_expense(self):
        apply_expense(self)
