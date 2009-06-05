from django.shortcuts import get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.db import connection
from django.template import RequestContext

from wallet import models as wallet


@permission_required('wallet.can_view_wallet_report')
def wallet_report(request):
    cursor = connection.cursor()
    context = {}
    cursor.execute("SELECT SUM(value) FROM wallet_transaction")
    context['totals'] = []
    context['totals'].append(('Total', cursor.fetchone()[0]))
    cursor.execute("SELECT SUM(value) FROM wallet_transaction WHERE VALUE > 0.0")
    context['totals'].append(('Deposit Total', cursor.fetchone()[0]))
    cursor.execute("SELECT SUM(value) FROM wallet_transaction WHERE VALUE < 0.0")
    context['totals'].append(('Withdraw Total', cursor.fetchone()[0]))
    cursor.execute("""SELECT u.username, SUM(t.value) as sum
    FROM wallet_transaction t
    JOIN wallet_wallet w ON (w.id = t.wallet_id)
    JOIN auth_user u ON (u.id = w.user_id)
    GROUP BY u.username
    ORDER BY sum DESC""")
    context['users'] = cursor.fetchall()
    return render_to_response(
        'wallet/report.html',
        context,
        context_instance=RequestContext(request),
    )


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
