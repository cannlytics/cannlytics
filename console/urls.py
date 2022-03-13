"""
URLs | Cannlytics Console
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 4/18/2021
Updated: 1/13/2022
License: License: MIT License <https://github.com/cannlytics/cannlytics-console/blob/main/LICENSE>

Resources: https://docs.djangoproject.com/en/3.2/topics/http/urls/
"""
# pylint:disable=invalid-name,unused-import

# External imports
from django.conf.urls import handler404, handler500
from django.urls import include, path

# Internal imports
from console.settings import DEBUG
from console.views import (
    auth,
    data,
    email,
    main,
    payments,
)

app_name = 'console'
main_view = main.ConsoleView.as_view()
urlpatterns = [
    path('', main_view, name='index'),
    path('account/<slug:page>', auth.LoginView.as_view(), name='auth'),
    path('api/', include('api.urls'), name='api'),
    path('src/', include([
        path('auth/login', auth.login),
        path('auth/logout', auth.logout),
        path('data/download', data.download_csv_data),
        path('data/import', data.import_data, name='import_data'),
        path('email/invite-user', email.invite_user),
        path('email/send-message', email.send_message),
        path('payments/subscribe', payments.subscribe),
    ])),
    path('<screen>', main_view, name='screen'),
    path('<screen>/<section>', main_view, name='section'),
    path('<screen>/<section>/<unit>', main_view, name='unit'),
    path('<screen>/<section>/<unit>/<part>', main_view, name='part'),
    path('<screen>/<section>/<unit>/<part>/<piece>', main_view, name='piece'),
]

# Error pages.
handler404 = 'console.views.main.handler404'
handler500 = 'console.views.main.handler500'

# Handle livereload during development.
if DEBUG:
    urlpatterns.insert(0, path('livereload', main.no_content))
