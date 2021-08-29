"""
URLs | Cannlytics Console
Created: 4/18/2021
Updated: 7/17/2021
Resources: https://docs.djangoproject.com/en/3.2/topics/http/urls/
"""
# pylint:disable=invalid-name,unused-import

# External imports
from django.conf.urls import handler404, handler500
from django.urls import include, path

# Internal imports
from console.views import (
    auth,
    data,
    email,
    main,
)

app_name = 'console'
urlpatterns = [
    path('', main.ConsoleView.as_view(), name='index'),
    path('account/<slug:page>', auth.LoginView.as_view(), name='auth'),
    path('api/', include('api.urls'), name='api'),
    path('download', data.download_csv_data),
    path('import', data.import_data, name='import_data'),
    path('livereload', main.no_content),
    path('login', auth.login),
    path('logout', auth.logout),
    path('send-feedback', email.send_feedback),
    path('src', include([
        path('/subscribe', email.subscribe),
    ])),
    path('<slug:screen>', main.ConsoleView.as_view()),
    path('<slug:screen>/<str:section>', main.ConsoleView.as_view()),
    path('<slug:screen>/<str:section>/<str:unit>', main.ConsoleView.as_view()),
    path('<slug:screen>/<str:section>/<str:unit>/<str:part>', main.ConsoleView.as_view()),
    path('<slug:screen>/<str:section>/<str:unit>/<str:part>/<str:piece>', main.ConsoleView.as_view()),
]

# Error pages.
handler404 = 'console.views.main.handler404'
handler500 = 'console.views.main.handler500'
