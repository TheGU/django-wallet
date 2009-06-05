import logging
import datetime
from decimal import Decimal

from django.conf import settings
from django.db import models, connection
from django.contrib.auth.models import User


class Overdraft(Exception):
    pass


logger = logging.getLogger('wallet')
handler = logging.StreamHandler()
formatter = logging.Formatter(
    "%(asctime)s %(levelname)-8s --- %(message)s"
)
handler.setFormatter(formatter)
if not getattr(settings, 'WALLET_LOGGER', True):
    handler.setHandler(logging.ERROR)
logger.addHandler(handler)


class Wallet(models.Model):
    user = models.ForeignKey(User, unique=True, related_name='wallets')
    
    def __unicode__(self):
        return "%s's wallet" % self.user.username
    
    def get_balance(self):
        cursor = connection.cursor()
        cursor.execute(
            "SELECT SUM(value) FROM wallet_transaction WHERE wallet_id = %s",
            (self.id,)
        )
        value = cursor.fetchone()[0]
        if value is None:
            value = Decimal('0.0')
        return value
    
    def withdraw(self, value, allow_overdraft=False):
        if not isinstance(value, int) and not isinstance(value, Decimal):
            raise ValueError("Value must be a Python int or Decimal")
        if value < 0:
            raise ValueError("You can't withdraw a negative amount")
        if not allow_overdraft and (self.get_balance() - value) < 0:
            raise Overdraft
        return self.transactions.create(
            date=datetime.datetime.now(),
            value=value * Decimal('-1.0'),
        )
    
    def deposit(self, value):
        if not isinstance(value, int) and not isinstance(value, Decimal):
            raise ValueError("Value must be a Python int or Decimal")
        if value < 0:
            raise ValueError("You can't deposit a negative amount")
        return self.transactions.create(
            date=datetime.datetime.now(),
            value=value,
        )


class Transaction(models.Model):
    wallet = models.ForeignKey(Wallet, related_name='transactions')
    date = models.DateTimeField()
    value = models.DecimalField(max_digits=20, decimal_places=2)
    notes = models.TextField(null=True, blank=True)
    
    def __unicode__(self):
        return str(self.value)


class PaymentOption(models.Model):
    name = models.CharField(max_length=255)
    dollar_amount = models.DecimalField(max_digits=20, decimal_places=2)
    wallet_amount = models.DecimalField(max_digits=20, decimal_places=2)
    enabled = models.BooleanField(default=True)
    
    def __unicode__(self):
        return '%s ($%.2f)' % (self.name, self.dollar_amount)


class Invoice(models.Model):
    user = models.ForeignKey(User, related_name='wallet_invoices')
    option = models.ForeignKey(PaymentOption, related_name='invoices')
    date_billed = models.DateTimeField()
    transaction = models.ForeignKey(
        Transaction,
        related_name='invoices',
        null=True,
        blank=True,
        unique=True,
    )
