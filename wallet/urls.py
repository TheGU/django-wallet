from django.conf.urls.defaults import *

from wallet import views


urlpatterns = patterns('',
    url(
        r'^deposit/(?P<option_id>\d+)/return/(?P<invoice_id>\d+)/$',
        views.deposit_return,
        name='deposit_return',
    ),
    url(
        r'^deposit/(?P<option_id>\d+)/return/(?P<invoice_id>\d+)/cancel/$',
        views.deposit_cancel,
        name='deposit_cancel',
    ),
)
