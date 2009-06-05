import urllib
import datetime
import urlparse

from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseRedirect, Http404
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse

from paypal.standard.forms import PayPalPaymentsForm
from paypal.standard.conf import POSTBACK_ENDPOINT, SANDBOX_POSTBACK_ENDPOINT

from wallet import models as wallet


@login_required
@transaction.commit_on_success
def deposit(request, option_id):
    option = get_object_or_404(wallet.PaymentOption, pk=option_id)
    invoice = request.user.wallet_invoices.create(
        option=option,
        date_billed=datetime.datetime.now(),
    )
    domain = Site.objects.get_current().domain
    return_url = reverse('deposit_return', args=[option.id, invoice.id])
    cancel_url = reverse('deposit_cancel', args=[option.id, invoice.id])
    paypal_data = {
        'cmd': '_xclick',
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': option.dollar_amount,
        'item_name': option.name,
        'invoice': invoice.id,
        'notify_url': urlparse.urljoin(domain, reverse('paypal-ipn')),
        'return_url': urlparse.urljoin(domain, return_url),
        'cancel_return': urlparse.urljoin(domain, cancel_url),
        'rm': '2',
        'no_shipping': '1',
        'no_note': '1',
        'currency_code': 'USD',
        'lc': 'US',
        'bn': 'PP-BuyNowBF',
        'charset': 'UTF-8',
    }
    query = urllib.urlencode(paypal_data)
    if getattr(settings, 'PAYPAL_SANDBOX', True):
        url = SANDBOX_POSTBACK_ENDPOINT
    else:
        url = POSTBACK_ENDPOINT
    return HttpResponseRedirect('%s?%s' % (url, query))


@login_required
def deposit_return(request, option_id, invoice_id):
    option = get_object_or_404(wallet.PaymentOption, pk=option_id)
    try:
        invoice = request.user.wallet_invoices.get(
            id=invoice_id,
            option=option,
        )
    except wallet.Invoice.DoesNotExist:
        raise Http404
    return HttpResponseRedirect(reverse('profile_detail'))


@login_required
def deposit_cancel(request, option_id, invoice_id):
    option = get_object_or_404(wallet.PaymentOption, pk=option_id)
    try:
        invoice = request.user.wallet_invoices.get(
            id=invoice_id,
            option=option,
        )
    except wallet.Invoice.DoesNotExist:
        raise Http404
    return HttpResponseRedirect(reverse('profile_detail'))
