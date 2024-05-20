"""This is the service module for the splitWise app."""

def add_owed(wallet, user_id, amount):
    user_id = str(user_id)
    if user_id in wallet.owes:
        wallet.owes[user_id] += amount
        if wallet.owes[user_id] <= 0:
            del wallet.owes[user_id]
    else:
        if user_id in wallet.is_owed:
            wallet.is_owed[user_id] -= amount
            if wallet.is_owed[user_id] <= 0:
                del wallet.is_owed[user_id]
        else:
            wallet.owes[user_id] = amount
    wallet.save()

def add_is_owed(wallet, user_id, amount):
    user_id = str(user_id)
    if user_id in wallet.is_owed:
        wallet.is_owed[user_id] += amount
        if wallet.is_owed[user_id] <= 0:
            del wallet.is_owed[user_id]
        else:
            if user_id in wallet.owes:
                wallet.owes[user_id] -= amount
                if wallet.owes[user_id] <= 0:
                    del wallet.owes[user_id]
            else:
                wallet.is_owed[user_id] = amount
    wallet.save()

def check_balance(Cls, wallet):
    if not wallet.is_owed:
        return "No balance"
    else:
        result = ""
        for debtor_id, amount in wallet.is_owed.items():
            debtor = Cls.objects.get(user_id=debtor_id)  # Fetch the User instance
            result += f"{wallet.owner.username} owes {debtor.username}: ${amount}\n"
        return result.strip()


def calculate_expense_sharing_values(expense_sharing):
    # Check if split_with field has users
    if expense_sharing.split_with.exists():
        if expense_sharing.method == "EQUAL":
            expense_sharing.values = [round(expense_sharing.expense.amount / expense_sharing.split_with.count(), 2)] * expense_sharing.split_with.count()
        elif expense_sharing.method == "EXACT":
            if sum(expense_sharing.values) != expense_sharing.expense.amount:
                raise ValueError("Total exact amounts must equal the total amount")
        elif expense_sharing.method == "PERCENT":
            total_percent = sum(expense_sharing.values)
            if total_percent != 100:
                raise ValueError("Total percentage must be 100")
            expense_sharing.values = [round(amount / 100 * expense_sharing.expense.amount, 2) for amount in expense_sharing.values]
        return True
    else:
        raise ValueError("No users to split the expense with")

def apply_expense(expense_sharing):
    from models import UserWallet
    for i, user in enumerate(expense_sharing.split_with.all()):
        payer = expense_sharing.expense.paid_by
        if user != payer:
            user_wallet, _ = UserWallet.objects.get_or_create(owner=user)
            payer_wallet, _ = UserWallet.objects.get_or_create(owner=payer)
            user_wallet.add_owed(payer_wallet.owner_id, expense_sharing.values[i])
            payer_wallet.add_is_owed(user_wallet.owner_id, expense_sharing.values[i])