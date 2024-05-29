from django.db import models
from uuid import uuid4
from django.contrib.auth import get_user_model
from UserApp.models import BaseModel

User = get_user_model()


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
