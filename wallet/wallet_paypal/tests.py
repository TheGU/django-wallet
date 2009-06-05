import unittest
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
