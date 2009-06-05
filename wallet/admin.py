from django.contrib import admin

from wallet import models as wallet


class WalletAdmin(admin.ModelAdmin):
    list_display = ('user',)
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
    ordering = ('-date',)
    date_hierarchy = 'date'
admin.site.register(wallet.Transaction, TransactionAdmin)


class PaymentOptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'dollar_amount', 'wallet_amount', 'enabled')
    list_filter = ('enabled',)
    ordering = ('dollar_amount',)
admin.site.register(wallet.PaymentOption, PaymentOptionAdmin)


class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'date_billed', 'option', 'user', 'transaction')
    date_hierarchy = 'date_billed'
    list_filter = ('date_billed', 'option')
    ordering = ('-date_billed',)
    search_fields = (
        'user__first_name',
        'user__last_name',
        'user__username',
        'user__email',
    )
admin.site.register(wallet.Invoice, InvoiceAdmin)
