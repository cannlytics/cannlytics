"""
URLs | Cannlytics Website
Copyright (c) 2020-2024 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 12/29/2020
Updated: 1/21/2024
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>
"""
# External imports:
from django.conf import settings
from django.conf.urls import handler404, handler500
from django.urls import include, path
from django.views.generic.base import RedirectView
from django_robohash.views import robohash

# Internal imports:
from website.views import (
    auth,
    main,
    payments,
)


# Main URLs.
urlpatterns = [
    path('', main.GeneralView.as_view(), name='index'),
    path('api/', include('api.urls'), name='api'),
    path('src/', include([
        path('auth/login', auth.login),
        path('auth/logout', auth.logout),
        path('payments/subscriptions', payments.get_user_subscriptions),
        path('payments/unsubscribe', payments.unsubscribe),
        path('payments/orders', payments.create_order, name='create_order'),
        path('payments/orders/<str:order_id>/capture', payments.capture_order, name='capture_order'),
    ])),
    path('donate', main.donate, name='donate'),
    path('meetup', main.meetup, name='meetup'),
    path('subscriptions', RedirectView.as_view(url='/account/subscriptions', permanent=False)),
    path('support', RedirectView.as_view(url='/account/subscriptions', permanent=False)),
    # path('videos', videos.VideosView.as_view(), name='videos'),
    # path('videos/<video_id>', videos.VideosView.as_view(), name='video'),
    path('.well-known/ai-plugin.json', RedirectView.as_view(url='/static/ai-plugin.json', permanent=False)),
    path('favicon.ico', RedirectView.as_view(url='/static/favicon.ico', permanent=False)),
    path('robots.txt', RedirectView.as_view(url='/static/robots.txt', permanent=False)),
    path('robohash/<string>', robohash, name='robohash'),
    path('<page>', main.GeneralView.as_view(), name='page'),
    path('<page>/<section>', main.GeneralView.as_view(), name='section'),
    path('<page>/<section>/<str:unit>', main.GeneralView.as_view(), name='unit'),
]


# Serve static assets in development and production.
if settings.DEBUG:
    from django.conf.urls.static import static #pylint: disable=ungrouped-imports
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Error pages.
handler404 = 'website.views.main.handler404' #pylint: disable=invalid-name
handler500 = 'website.views.main.handler500' #pylint: disable=invalid-name
