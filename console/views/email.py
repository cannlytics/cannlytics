"""
Email Views | Cannlytics Console
Author: Keegan Skeate <keegan@cannlytics.com>
Created: 12/18/2020
Updated: 7/17/2021
"""

# Standard imports
from datetime import datetime
from json import loads

# External imports
from django.core.mail import send_mail
from django.http.response import JsonResponse

# Internal imports
from cannlytics.firebase import (
    update_document,
    verify_session_cookie,
)
from console.settings import (
    DEFAULT_FROM_EMAIL,
    LIST_OF_EMAIL_RECIPIENTS,
)


def send_feedback(request, *args, **argv): #pylint: disable=unused-argument
    """Send feedback from the console to the Cannlytics admin with email."""
    data = loads(request.body.decode('utf-8'))['data']
    name = data['name']
    subject = data['subject']
    message = data['message']
    sender = data['email']
    recipients = LIST_OF_EMAIL_RECIPIENTS
    if not sender:
        sender = DEFAULT_FROM_EMAIL
    text = 'New feedback on the Cannlytics Console'
    text += '\n\n{0}'.format(message)
    if name is not None:
        text += '\n\nFrom,\n' + str(name)
    send_mail(
        subject=subject.strip(),
        message=text,
        from_email=sender,
        recipient_list=recipients,
        fail_silently=False,
    )
    return JsonResponse({'success': True}, status=204)


def subscribe(request):
    """
    Subscribe a user to the Cannlytics platform,
    sending them an email with the ability to unsubscribe.
    """
    data = loads(request.body.decode('utf-8'))
    session_cookie = request.COOKIES.get('__session')
    claims = verify_session_cookie(session_cookie)
    data = {**data, ** claims}
    uid = claims['uid']
    user_email = claims['email']
    now = datetime.now()
    iso_time = now.isoformat()
    data['created_at'] = iso_time
    data['updated_at'] = iso_time
    update_document(f'admin/paypal/paypal_subscriptions/{uid}', data)
    # Optional: Send HTML message.
    # template_url = "cannlytics_website/emails/newsletter_subscription_thank_you.html"
    send_mail(
        subject='You are now subscribed to Cannlytics, congratulations!',
        message='Congratulations,\n\nWelcome to the Cannlytics platform. You can hit the docs at docs.cannlytics.com or begin testing the functionality.\n\nYou will receive notifications for important updates and changes.\n\nAlways here to help,\nThe Cannlytics Team',
        from_email="contact@cannlytics.com",
        recipient_list=[user_email],
        fail_silently=False,
        # html_message = render_to_string(template_url, {"context": "values"}) # Optional: Send HTML email
    )
    return JsonResponse({'success': True}, safe=False)
