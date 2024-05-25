from rest_framework import serializers
from .models import Expense, ExpenseSharing, User, UserWallet

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = ['id', 'paid_by', 'title', 'description', 'amount']


class ExpenseSharingSerializer(serializers.ModelSerializer):
    total_shares = serializers.ReadOnlyField()
    class Meta:
        model = ExpenseSharing
        exclude = ['paid_by']



class ExpenseSharingSerializer(serializers.ModelSerializer):
    expense = serializers.PrimaryKeyRelatedField(queryset=Expense.objects.all())
    split_with = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
    total_shares = serializers.ReadOnlyField()
    
    class Meta:
        model = ExpenseSharing
        fields = ['expense', 'method', 'split_with','total_shares']


