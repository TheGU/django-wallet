from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse

from wallet import models as wallet


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
    request.user.message_set.create(message='Thank you for your payment!')
    return HttpResponseRedirect('/')


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
    request.user.message_set.create(message='Payment cancelled')
    return HttpResponseRedirect('/')
