from django.contrib import admin
from .models import Wallet, Transaction

# Register Wallet model
@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'created_at')
    search_fields = ('user__username',)

# Register Transaction model
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'transaction_type', 'transaction_purpose')
    search_fields = ('wallet__user__username',)
    list_filter = ('transaction_type', 'transaction_purpose')
