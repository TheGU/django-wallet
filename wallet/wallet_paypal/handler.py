import logging

from django.conf import settings

from paypal.standard.ipn.signals import payment_was_successful

from wallet.models import Invoice


logger = logging.getLogger('wallet')
handler = logging.StreamHandler()
formatter = logging.Formatter(
    "%(asctime)s %(levelname)-8s --- %(message)s"
)
handler.setFormatter(formatter)
if not getattr(settings, 'PAYPAL_SANDBOX', True):
    handler.setHandler(logging.ERROR)
logger.addHandler(handler)


def wallet_deposit(sender, **kwargs):
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
