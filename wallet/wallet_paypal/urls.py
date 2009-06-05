from django.conf.urls.defaults import *

from wallet.wallet_paypal import views


urlpatterns = patterns('',
    url(
        r'^options/$',
        views.options,
        name='wallet_paypal_options',
    ),
    url(
        r'^deposit/(?P<option_id>\d+)/$',
        views.deposit,
        name='wallet_paypal_deposit',
    ),
)
