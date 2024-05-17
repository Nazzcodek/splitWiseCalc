from django.db import models
from uuid import uuid4

class User(models.Model):
    user_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username


class Expense(models.Model):
    transaction_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    paid_by = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.amount}"


class UserWallet(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    owes = models.JSONField(default=dict)
    is_owed = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def add_owed(self, user_id, amount):
        user_id = str(user_id)
        if user_id in self.owes:
            self.owes[user_id] += amount
            if self.owes[user_id] <= 0:
                del self.owes[user_id]
        else:
            if user_id in self.is_owed:
                self.is_owed[user_id] -= amount
                if self.is_owed[user_id] <= 0:
                    del self.is_owed[user_id]
            else:
                self.owes[user_id] = amount
        self.save()

    def add_is_owed(self, user_id, amount):
        user_id = str(user_id)
        if user_id in self.is_owed:
            self.is_owed[user_id] += amount
            if self.is_owed[user_id] <= 0:
                del self.is_owed[user_id]
        else:
            if user_id in self.owes:
                self.owes[user_id] -= amount
                if self.owes[user_id] <= 0:
                    del self.owes[user_id]
            else:
                self.is_owed[user_id] = amount
        self.save()

    def check_balance(self):
        if not self.is_owed:
            return "No balance"
        else:
            result = ""
            for debtor_id, amount in self.is_owed.items():
                debtor = User.objects.get(user_id=debtor_id)  # Fetch the User instance
                result += f"{self.owner.username} owes {debtor.username}: ${amount}\n"
            return result.strip()

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

        # Check if split_with field has users
        if self.split_with.exists():
            if self.method == "EQUAL":
                self.values = [round(self.expense.amount / self.split_with.count(), 2)] * self.split_with.count()
            elif self.method == "EXACT":
                if sum(self.values) != self.expense.amount:
                    raise ValueError("Total exact amounts must equal the total amount")
            elif self.method == "PERCENT":
                total_percent = sum(self.values)
                if total_percent != 100:
                    raise ValueError("Total percentage must be 100")
                self.values = [round(amount / 100 * self.expense.amount, 2) for amount in self.values]

            self.apply_expense()
        else:
            raise ValueError("No users to split the expense with")

        # Save again to update any changes
        super().save(*args, **kwargs)

    def apply_expense(self):
        for i, user in enumerate(self.split_with.all()):
            payer = self.expense.paid_by
            if user != payer:
                user_wallet, _ = UserWallet.objects.get_or_create(owner=user)
                payer_wallet, _ = UserWallet.objects.get_or_create(owner=payer)
                user_wallet.add_owed(payer_wallet.owner_id, self.values[i])
                payer_wallet.add_is_owed(user_wallet.owner_id, self.values[i])
