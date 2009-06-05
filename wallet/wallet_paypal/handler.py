import logging

from paypal.standard.ipn.signals import payment_was_successful

from wallet.models import Invoice


def wallet_deposit(sender, **kwargs):
    logger = logging.getLogger('wallet')
    logger.debug('PayPal Signal Handler')
    invoice_id = sender.invoice
    invoice_id = int(invoice_id)
    logger.debug('Invoice ID: %d' % invoice_id)
    invoice = Invoice.objects.get(id=invoice_id)
    logger.debug('Invoice: %s' % invoice)
    wallet = invoice.user.wallets.all()[0]
    logger.debug('Wallet: %s' % wallet)
    invoice.transaction = wallet.deposit(invoice.option.wallet_amount)
    invoice.save()
    logger.debug('PayPal IPN Complete')
payment_was_successful.connect(wallet_deposit)
