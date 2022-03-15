"""
URLs | Cannlytics Website
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 12/29/2020
Updated: 1/20/2022
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>
"""
# External imports.
from django.conf import settings
from django.conf.urls import handler404, handler500 #pylint: disable=unused-import
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
    subscriptions,
    testing,
    videos,
)

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
        # TODO: Implement blockchain market functionality
        # path('market/buy', market.buy_data),
        # path('market/publish', market.publish_data),
        # path('market/sell', market.sell_data),
        path('market/buy-data', market.buy_data),
        path('payments/subscribe', subscriptions.subscribe, name='subscribe'),
        path('payments/subscriptions', subscriptions.get_user_subscriptions),
        path('payments/unsubscribe', subscriptions.unsubscribe),
    ])),
    # path('data', include([
    #     path('', main.GeneralView.as_view(), name='data'),
    #     path('/market', main.GeneralView.as_view(), name='market'),
    #     path('/<dataset_id>', market.DatasetView.as_view(), name='dataset'),
    # ])),
    path('data/market/<dataset_id>', market.DatasetView.as_view(), name='dataset'),
    path('testing', include([
        path('', testing.TestingView.as_view(), name='testing'),
        path('/labs', testing.TestingView.as_view(), name='labs'),
        path('/labs/new', testing.NewLabView.as_view(), name='new-lab'),
        path('/labs/<lab>', testing.LabView.as_view(), name='lab'),
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
    path('labs', RedirectView.as_view(url='/testing/labs', permanent=False)),
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
