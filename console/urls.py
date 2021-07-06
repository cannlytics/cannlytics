"""
URLs | Cannlytics
Created: 4/18/2021
Updated: 7/6/2021
Resources: https://docs.djangoproject.com/en/3.2/topics/http/urls/
"""

# External imports
from django.conf.urls import handler404, handler500
from django.urls import include, path


# Internal imports
from console import views

app_name = 'console' # pylint: disable=invalid-name
urlpatterns = [
    path('', views.ConsoleView.as_view(), name='index'),
    path('account/<slug:page>', views.LoginView.as_view(), name='auth'),
    path('api/', include('api.urls'), name='api'),
    path('download', views.download_csv_data),
    path('import', views.import_data, name='import_data'),
    path('livereload', views.no_content),
    path('login', views.login),
    path('logout', views.logout),
    path('<slug:screen>', views.ConsoleView.as_view()),
    path('<slug:screen>/<slug:section>', views.ConsoleView.as_view()),
    path('<slug:screen>/<slug:section>/<slug:unit>', views.ConsoleView.as_view()),
    path('<slug:screen>/<slug:section>/<slug:unit>/<slug:collection>', views.ConsoleView.as_view()),
    path('<slug:screen>/<slug:section>/<slug:unit>/<slug:collection>/<slug:document>', views.ConsoleView.as_view()),
]

# Error pages.
handler404 = 'console.views.handler404'
handler500 = 'console.views.handler500'

# Optional: Add 403 and 400 pages
# handler403 = 'console.views.my_custom_permission_denied_view'
# handler400 = 'console.views.my_custom_bad_request_view'
