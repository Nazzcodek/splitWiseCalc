"""This is the service module for the splitWise app."""

from .models import User, UserWallet, ExpenseSharing
from django.db import transaction

def add_owed(wallet, user_id, amount):
    user_id = str(user_id)
    wallet.balances.setdefault(user_id, 0)
    wallet.balances[user_id] += amount
    if wallet.balances[user_id] == 0:
        # Remove the user from the balances if the amount is 0
        del wallet.balances[user_id]
    wallet.save()


def add_is_owed(wallet, user_id, amount):
    add_owed(wallet, user_id, -amount)

def check_balance(wallet):
    if not wallet.balances:
        return "No balance"
    else:
        result = ""
        for user_id, amount in wallet.balances.items():
            debtor = User.objects.get(user_id=user_id)
            # Check if the user is owed to the wallet or owes to the wallet
            # user is debitor
            if amount > 0:
                result += f"{wallet.owner.username} owes {debtor.username}: ${amount}\n"
            # user is creditor
            elif amount < 0:
                result += f"{debtor.username} owes {wallet.owner.username}: ${-amount}\n"
        return result.strip()


def calculate_expense_sharing_values(expense_sharing):
    amount = expense_sharing.expense.amount
    num_shares = expense_sharing.total_shares

    if expense_sharing.method == "EQUAL":
        return [round(amount / num_shares, 2)] * num_shares
    elif expense_sharing.method == "EXACT":
        if sum(expense_sharing.values) != amount:
            raise ValueError("Total exact amounts must equal the total amount")
        return expense_sharing.values
    elif expense_sharing.method == "PERCENT":
        total_percent = sum(expense_sharing.values)
        if total_percent != 100:
            raise ValueError("Total percentage must be 100")
        return [round(percent / 100 * amount, 2) for percent in expense_sharing.values]
    else:
        raise ValueError("Invalid splitting method")

# I'm using transaction for data consistency so balances are updated atomically
@transaction.atomic  
def apply_expense(expense_sharing):
    shares = calculate_expense_sharing_values(expense_sharing)  

    for i, user in enumerate(expense_sharing.split_with.all()):
        if user != expense_sharing.expense.paid_by:
            user_wallet, _ = UserWallet.objects.get_or_create(owner=user)
            payer_wallet, _ = UserWallet.objects.get_or_create(owner=expense_sharing.expense.paid_by)
            user_wallet.update_balance(payer_wallet.owner_id, shares[i])
            payer_wallet.update_balance(user_wallet.owner_id, -shares[i])
