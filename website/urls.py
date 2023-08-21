"""
URLs | Cannlytics Website
Copyright (c) 2020-2023 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 12/29/2020
Updated: 6/20/2023
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>
"""
# External imports.
from django.conf import settings
from django.conf.urls import handler404, handler500
from django.http import HttpResponse #pylint: disable=unused-import
from django.urls import include, path
from django.views.generic.base import RedirectView
from django_robohash.views import robohash

# Internal imports.
from website.views import (
    auth,
    data,
    email,
    main,
    market,
    payments,
    testing,
    videos,
)


def read_file(request):
    """Read a file from the filesystem."""
    # TODO: Test if this works:
    # os.path.join(os.path.dirname(__file__), 'openapi.yaml')
    f = open('static/ai-plugin.json', 'r')
    file_content = f.read()
    f.close()
    return HttpResponse(file_content, content_type='text/plain')


# Main URLs.
urlpatterns = [
    path('', main.GeneralView.as_view(), name='index'),
    path('api/', include('api.urls'), name='api'),
    path('src/', include([
        path('auth/login', auth.login),
        path('auth/logout', auth.logout),
        path('data/download-analyses-data', data.download_analyses_data),
        path('data/download-lab-data', data.download_lab_data),
        path('data/download-regulation-data', data.download_regulation_data),
        path('email/send-message', email.send_message, name="message"),
        path('email/suggest-edit', email.suggest_edit, name="suggestion"),
        path('market/promotions', market.promotions, name='promotions'),
        # TODO: Implement blockchain data market functionality.
        # path('market/buy', market.buy_data),
        # path('market/publish', market.publish_data),
        # path('market/sell', market.sell_data),
        path('market/buy-data', market.buy_data),
        path('payments/subscriptions', payments.get_user_subscriptions),
        path('payments/unsubscribe', payments.unsubscribe),
        path('payments/orders', payments.create_order, name='create_order'),
        path('payments/orders/<str:order_id>/capture', payments.capture_order, name='capture_order'),
    ])),
    # Optional: Redirect data/wa or data/washington to data/states/washington?
    path('data/market/<dataset_id>', market.DatasetView.as_view(), name='dataset'),
    path('testing', include([
        path('', testing.TestingView.as_view(), name='testing'),
        path('labs', testing.TestingView.as_view(), name='labs'),
        path('labs/new', testing.NewLabView.as_view(), name='new-lab'),
        path('labs/<lab>', testing.LabView.as_view(), name='lab'),
        # TODO: Add regulation and analysis specific pages.
        # path('/analyses', testing.TestingView.as_view(), name='analyses'),
        # path('/analyses/<analysis_id>', testing.TestingView.as_view(), name='analysis'),
        # path('/regulations', testing.TestingView.as_view(), name='regulations'),
        # path('/regulations/<state>', testing.TestingView.as_view(), name='regulation'),
    ])),
    path('robohash/<string>', robohash, name='robohash'),
    path('videos', videos.VideosView.as_view(), name='videos'),
    path('videos/<video_id>', videos.VideosView.as_view(), name='video'),
    path('meetup', main.meetup, name='meetup'),
    path('community', RedirectView.as_view(url='/testing', permanent=False)),
    path('effects', RedirectView.as_view(url='/stats/effects', permanent=False)),
    path('labs', RedirectView.as_view(url='/testing/labs', permanent=False)),
    path('<page>', main.GeneralView.as_view(), name='page'),
    path('<page>/<section>', main.GeneralView.as_view(), name='section'),
    path('<page>/<section>/<str:unit>', main.GeneralView.as_view(), name='unit'),
    path('.well-known/ai-plugin.json', read_file),
]


# Serve static assets in development and production.
if settings.DEBUG:
    from django.conf.urls.static import static #pylint: disable=ungrouped-imports
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Error pages.
handler404 = 'website.views.main.handler404' #pylint: disable=invalid-name
handler500 = 'website.views.main.handler500' #pylint: disable=invalid-name
