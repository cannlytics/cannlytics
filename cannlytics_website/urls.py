"""
URLs | Cannlytics Website
Created: 12/29/2020
Resources: https://docs.djangoproject.com/en/3.1/topics/http/urls/
"""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django_robohash.views import robohash
from . import api, views


# Main URLs
urlpatterns = [
    path('', views.GeneralView.as_view(), name='index'),
    path('admin/', admin.site.urls, name='admin'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('community/', views.CommunityView.as_view(), name='community'),
    path('api/', include('cannlytics_api.urls'), name='api'),
    path('docs/', include('cannlytics_docs.urls'), name='docs'),
    path('labs/', views.CommunityView.as_view(), name='labs'),  # Redundant
    path('labs/new/', views.NewLabView.as_view()),
    path('labs/<slug:lab>/', views.LabView.as_view()),
    # path('labs\.json', views.CommunityView.as_view()),
    # path('labs/<slug:lab>/.json', views.LabView.as_view())
    path('download-lab-data/', api.download_lab_data),
    path('robohash/<string>/', robohash, name='robohash'),
    path('subscribe/', api.subscribe, name='subscribe'),
    path('promotions/', api.promotions, name='promotions'),

    # TODO: Add articles!
    path('articles/', api.promotions, name='articles'),
    path('articles/<slug:section>/', api.promotions, name='articles'),

    # TODO: Add video archive!
    path('videos/', api.promotions, name='videos'),
    path('videos/<slug:section>/', api.promotions, name='video'),

    # path('captcha/', include('captcha.urls')),
    path('<slug:page>/', views.GeneralView.as_view(), name='page'),
    path('<slug:page>/<slug:section>/', views.GeneralView.as_view(), name='section'),
]

# Serve static assets in development and production.
if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
