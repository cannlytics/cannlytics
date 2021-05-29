"""
URLs | Cannlytics
Created: 4/18/2021
Updated: 4/30/2021
Resources: https://docs.djangoproject.com/en/3.2/topics/http/urls/
"""

# External imports
from django.conf.urls import handler404, handler500
from django.urls import include, path


# Internal imports
from cannlytics_console import views

app_name = 'cannlytics_console' # pylint: disable=invalid-name
urlpatterns = [
    path('', views.ConsoleView.as_view(), name='index'),
    path('account/<slug:page>', views.LoginView.as_view(), name='auth'),
    path('api/', include('cannlytics_api.urls'), name='api'),
    # HACK: Handle livereload during development.
    path('livereload', views.no_content),
    # TODO: Merge website links as /about or redirect common pages
    path('<slug:screen>', views.ConsoleView.as_view()),
    path('<slug:screen>/<slug:section>', views.ConsoleView.as_view()),
    path('<slug:screen>/<slug:section>/<slug:unit>', views.ConsoleView.as_view()),
]

# Error pages.
handler404 = 'cannlytics_console.views.handler404'
handler500 = 'cannlytics_console.views.handler500'

# Optional: Add 403 and 400 pages
# handler403 = 'cannlytics_console.views.my_custom_permission_denied_view'
# handler400 = 'cannlytics_console.views.my_custom_bad_request_view'
