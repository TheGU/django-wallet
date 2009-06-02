import datetime
from decimal import Decimal

from django.db import models, connection
from django.contrib.auth.models import User


class Overdraft(Exception):
    pass


class Wallet(models.Model):
    user = models.ForeignKey(User, related_name='wallets')
    
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
        if isinstance(value, float):
            raise ValueError("Value must be a Python int or Decimal")
        if value < 0:
            raise ValueError("You can't withdraw a negative amount")
        if not allow_overdraft and (self.get_balance() - value) < 0:
            raise Overdraft
        self.transactions.create(
            date=datetime.datetime.now(),
            value=value * Decimal('-1.0'),
        )
    
    def deposit(self, value):
        if isinstance(value, float):
            raise ValueError("Value must be a Python int or Decimal")
        if value < 0:
            raise ValueError("You can't deposit a negative amount")
        self.transactions.create(
            date=datetime.datetime.now(),
            value=value,
        )


class Transaction(models.Model):
    wallet = models.ForeignKey(Wallet, related_name='transactions')
    date = models.DateTimeField()
    value = models.DecimalField(max_digits=20, decimal_places=2)
    notes = models.TextField(null=True)
    
    def __unicode__(self):
        return str(self.value)
