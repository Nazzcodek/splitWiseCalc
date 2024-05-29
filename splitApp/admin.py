from django.contrib import admin
from .models import Expense, UserWallet, ExpenseSharing



class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('id', 'transaction_id', 'title', 'paid_by', 'amount', 'created_at', 'updated_at')
    search_fields = ('title', 'paid_by__username')
    readonly_fields = ('transaction_id', 'created_at', 'updated_at')

class UserWalletAdmin(admin.ModelAdmin):
    list_display = ('owner', 'balances', 'created_at', 'updated_at')
    search_fields = ('owner__username',)
    readonly_fields = ('created_at', 'updated_at')

class ExpenseSharingAdmin(admin.ModelAdmin):
    list_display = ('id', 'expense', 'method', 'total_shares', 'created_at', 'updated_at')
    search_fields = ('expense__title', 'method')
    readonly_fields = ('created_at', 'updated_at')
    exclude = ('created_at', 'updated_at')  # Exclude non-editable fields from forms



admin.site.register(Expense, ExpenseAdmin)
admin.site.register(UserWallet, UserWalletAdmin)
admin.site.register(ExpenseSharing, ExpenseSharingAdmin)
