from django.db import models
from uuid import uuid4


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


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
    # Added total shares field
    total_shares = models.PositiveIntegerField()
