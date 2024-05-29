"""This is the service module for the splitWise app."""
from splitApp.models import UserWallet
from django.db import transaction
from django.contrib.auth import get_user_model

User = get_user_model()





def update_balance(wallet, user_id, amount):
    """Updates the balance of a user in the wallet."""
    user_id = str(user_id) 
    print(f'user_id: {user_id}')
    wallet.balances.setdefault(user_id, 0)  
    wallet.balances[user_id] += float(amount)
    if wallet.balances[user_id] == 0:
        del wallet.balances[user_id]
    wallet.save()

def check_balance(wallet):
    if not wallet.balances:
        return "No balance"
    else:
        result = []
        for user_id, amount in wallet.balances.items():
            amount = round(amount,2)
            user = User.objects.get(id = user_id)
            # Check if the user is owed to the wallet or owes to the wallet
            # user is debitor


            if amount > 0:
                result.append({
                    'wallet_owner': wallet.owner.username,
                    'creditor': user.username,
                    'amount': amount,
                    'status': f"{wallet.owner.username} owes {user.username} ${amount}"
                })
            elif amount < 0:
                result.append({
                    'debtor': user.username,
                    'wallet_owner': wallet.owner.username,
                    'amount': -amount,
                    'status': f"{user.username} owes {wallet.owner.username}: ${-amount}"
                })
        return result


def calculate_expense_sharing_values(method, amount, values, total_shares):
    # Convert values to floats
    values = [float(value) for value in values]

    if method == "EQUAL":
        return [round(amount / total_shares, 2)] * total_shares
    elif method == "EXACT":
        if sum(values) != amount:
            raise ValueError("Total exact amounts must equal the total amount")
        return values
    elif method == "PERCENT":
        total_percent = sum(values)
        if total_percent != 100:
            raise ValueError("Total percentage must be 100")
        # Convert amount to float before performing multiplication
        return [round(percent / 100 * float(amount), 2) for percent in values]
    else:
        raise ValueError("Invalid splitting method")


# I'm using transaction for data consistency so balances are updated atomically
@transaction.atomic  
def apply_expense(expense_sharing, shares):
    split_with_users = list(expense_sharing.split_with.all())
    for i, user in enumerate(split_with_users):
        if user != expense_sharing.expense.paid_by:
            user_wallet, _ = UserWallet.objects.get_or_create(owner=user)
            payer_wallet, _ = UserWallet.objects.get_or_create(owner=expense_sharing.expense.paid_by)
            update_balance(user_wallet, payer_wallet.owner.id, shares[i])
            update_balance(payer_wallet, user_wallet.owner.id, -shares[i])
