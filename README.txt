django-wallet
=============

    django-wallet is a simple, pluggable django app supporting basic withdraws and deposits for users.  Users receive a single wallet (i.e. basic on-site bank account) to which they can transfer funds to and from.  [http://github.com/johnboxall/django-paypal/tree/master django-paypal] is optionally supported as well.

Installation
============
1) Download the app through SVN and add it to your Python path:

    ::
        
        svn co http://django-wallet.googlecode.com/svn/trunk/wallet wallet


2) Add to your INSTALLED_APPS

    ::

        INSTALLED_APPS = (
            # ...
            'wallet',
            'wallet.wallet_paypal', # optional
            'paypal.standard.ipn', # optional
            # ...
        )


3) Add the remotelog urls to your urls.py, e.g.:

    ::

        urlpatterns = patterns('',
            # ...
            url(r'^wallet/', include('wallet.urls')),
            url(r'^wallet/paypal/', include('wallet.wallet_paypal.urls')), # optional
            url(r'^paypal/ipn/', include('paypal.standard.ipn.urls')), # optional
            # ...
        )


4) Settings file:

    ::

        PAYPAL_TEST = False # or True for PayPal sandbox
        # receiver_email
        #   Primary email address of the payment recipient (that is, the merchant). If 
        #   the payment is sent to a non-primary email address on your PayPal 
        #   account, the receiver_email is still your primary email.
        PAYPAL_RECEIVER_EMAIL = "admin@example.com"
        # business
        #   Email address or account ID of the payment recipient (that is, the 
        #   merchant). Equivalent to the values of receiver_email (if payment is 
        #   sent to primary account) and business set in the Website Payment 
        #   HTML.
        PAYPAL_BUSINESS_EMAIL = "admin@example.com"


5) Run ./manage.py syncdb, log into the admin to add a Payment Option, then start your server and visit:

    http://localhost:8000/wallet/paypal/options/


Development sponsored by `Caktus Consulting Group, LLC
<http://www.caktusgroup.com/services>`_.
