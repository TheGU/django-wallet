from django.contrib import admin

from wallet import models as wallet


class WalletAdmin(admin.ModelAdmin):
    list_display = ('id', 'user')
    search_fields = (
        'wallet__user__first_name',
        'wallet__user__last_name',
        'wallet__user__username',
        'wallet__user__email',
    )
admin.site.register(wallet.Wallet, WalletAdmin)


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'wallet', 'date', 'value')
    list_filter = ('date',)
    search_fields = (
        'wallet__user__first_name',
        'wallet__user__last_name',
        'wallet__user__username',
        'wallet__user__email',
        'value',
    )
    ordering = ('date',)
    date_hierarchy = 'date'
admin.site.register(wallet.Transaction, TransactionAdmin)
