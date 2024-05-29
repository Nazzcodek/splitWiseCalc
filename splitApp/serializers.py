from rest_framework import serializers
from .models import Expense, ExpenseSharing
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=255)


class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = ['id', 'paid_by', 'title', 'description', 'amount', 'created_at', 'updated_at']


class ExpenseSharingSerializer(serializers.ModelSerializer):
    total_shares = serializers.ReadOnlyField()
    class Meta:
        model = ExpenseSharing
        exclude = ['paid_by']


class ExpenseSharingSerializer(serializers.ModelSerializer):
    expense = serializers.PrimaryKeyRelatedField(queryset=Expense.objects.all())
    split_with = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
    total_shares = serializers.ReadOnlyField()
    created_at = serializers.ReadOnlyField()
    updated_at = serializers.ReadOnlyField()

    class Meta:
        model = ExpenseSharing
        fields = ['expense', 'method', 'split_with','total_shares', 'created_at', 'updated_at']


class UserWalletSerializer(serializers.Serializer):
    wallet_owner = serializers.CharField()
    debtor= serializers.CharField(required = False)
    creditor = serializers.CharField(required = False)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    status = serializers.CharField()

