import random
import unittest
from decimal import Decimal
import urlparse
import datetime

from django.conf import settings
from django.test.client import Client
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from paypal.standard.ipn.tests import IPN_POST_PARAMS, DummyPayPalIPN
from paypal.standard.ipn.models import PayPalIPN
from paypal.standard.ipn.forms import PayPalIPNForm

from wallet import models as wallet


class WalletTestCase(unittest.TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            'user',
            'user@example.com',
            'abc123',
        )
        self.wallet = wallet.Wallet.objects.create(user=self.user)
    
    def tearDown(self):
        self.user.delete()
    
    def testDeposit(self):
        self.assertEqual(self.wallet.transactions.count(), 0)
        self.assertEqual(self.wallet.get_balance(), 0)
        self.wallet.deposit(200)
        self.assertEqual(self.wallet.transactions.count(), 1)
        self.assertEqual(self.wallet.get_balance(), 200)
    
    def testNegativeDepositWithdraw(self):
        value = random.randint(1, 100) * -1
        self.assertRaises(ValueError, self.wallet.deposit, value)
        self.assertRaises(ValueError, self.wallet.withdraw, value)
    
    def testFloat(self):
        value = random.uniform(1, 100)
        self.assertRaises(ValueError, self.wallet.deposit, value)
        self.assertRaises(ValueError, self.wallet.withdraw, value)
    
    def testWithdrawInteger(self):
        value = random.randint(1, 100)
        self.wallet.deposit(value)
        self.assertEqual(self.wallet.get_balance(), value)
        self.wallet.withdraw(value)
        self.assertEqual(self.wallet.get_balance(), 0)
    
    def testWithdrawDecimal(self):
        value = Decimal('%.2f' % random.uniform(1, 100))
        self.wallet.deposit(value)
        balance = self.wallet.get_balance()
        self.assertTrue(isinstance(balance, Decimal))
        self.assertEqual(balance, value)
        self.wallet.withdraw(value)
        balance = self.wallet.get_balance()
        self.assertTrue(isinstance(balance, Decimal))
        self.assertEqual(balance, 0)
    
    def testOverdraft(self):
        value1 = Decimal('%.2f' % random.uniform(1, 100))
        self.wallet.deposit(value1)
        value2 = Decimal('%.2f' % random.uniform(101, 200))
        self.assertRaises(wallet.Overdraft, self.wallet.withdraw, value2)
        self.wallet.withdraw(value2, True)
        self.assertEqual(self.wallet.get_balance(), value1 - value2)


class WalletPayPalTestCase(unittest.TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            'user',
            'user@example.com',
            'abc123',
        )
        self.wallet = wallet.Wallet.objects.create(user=self.user)
        self.client = Client()
    
    def tearDown(self):
        self.user.delete()
    
    def testInvalidDepositOption(self):
        self.assertEqual(wallet.PaymentOption.objects.count(), 0)
        self.client.login(username=self.user.username, password='abc123')
        response = self.client.get(reverse('wallet_deposit', args=[1000]))
        self.assertEqual(response.status_code, 404)
    
    def testDeposit(self):
        self.assertEqual(wallet.PaymentOption.objects.count(), 0)
        option = wallet.PaymentOption.objects.create(
            name='100 j$',
            dollar_amount=100,
            wallet_amount=200,
        )
        self.assertEqual(wallet.PaymentOption.objects.count(), 1)
        self.client.login(username=self.user.username, password='abc123')
        response = self.client.get(reverse('wallet_deposit', args=[option.id]))
        self.assertTrue('paypal.com' in response['Location'])
        invoice = wallet.Invoice.objects.all()[0]
        self.assertTrue('invoice=%d' % invoice.id in response['Location'])
        self.assertTrue('amount=%.2f' % option.dollar_amount in response['Location'])
