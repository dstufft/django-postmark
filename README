Django Postmark
===============

django-postmark is a reusable app that includes an EmailBackend for sending email
with Django as well as models and view that enable integration with Postmark's
bounce hook api.

Installation
------------

You can install django postmark with pip by typing::

    pip install django-postmark
    
Or with easy_install by typing::

    easy_install django-postmark
    
Or manually by downloading a tarball and typing::

    python setup.py install
    
Once installed add `postmark` to your `INSTALLED_APPS` and run::

    python manage.py syncdb
    
Django Configuration
--------------------

If you want to use django-postmark as your default backend, you should add::

    EMAIL_BACKEND = "postmark.backends.PostmarkBackend"

to your settings.py

Settings
--------

django-postmark adds 1 required setting and 2 optional settings.

Required:
    Specifies the api key for your postmark server.::

        POSTMARK_API_KEY = 'POSTMARK_API_TEST'
    
Optional:
    Specifies a username and password that the view will require to be passed
    in via basic auth. (http://exampleuser:examplepassword@example.com/postmark/bounce/)::
    
        POSTMARK_API_USER = "exampleuser"
        POSTMARK_API_PASSWORD = "examplepassword"
    
Postmark Bounce Hook
--------------------

Postmark has the optional ability to POST to an url anytime a message you have
sent bounces. django-postmark comes with an urlconf and view for this purpose. If
you wish to use this then add::

    url(r"^postmark/", include("postmark.urls")),
    
to your root urls.py. This will cause your bounce hook location to live
at /postmark/bounce/. Then simply add in the url to your Postmark settings (with
the username and password specified by POSTMARK_API_USER/PASSWORD if set) and
django will accept POSTS from Postmark notifying it of a new bounce.
