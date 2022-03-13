"""
Email Views | Cannlytics Console
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 12/18/2020
Updated: 1/13/2022
License: MIT License <https://github.com/cannlytics/cannlytics-console/blob/main/LICENSE>
"""
# Standard imports
from json import loads
from cannlytics.auth.auth import authenticate_request

# External imports
from django.core.mail import send_mail
from django.http.response import JsonResponse

# Internal imports
from console.settings import (
    DEFAULT_FROM_EMAIL,
    LIST_OF_EMAIL_RECIPIENTS,
)


def invite_user(request, *args, **argv): #pylint: disable=unused-argument
    """Invite a user to the Cannlytics console."""
    try:
        claims = authenticate_request(request)
        user_email = claims['email']
    except KeyError:
        return JsonResponse({'success': False, 'message': 'Unauthorized.'}, status=401)
    
    # FIXME: Implement logic to invite user to organization's team.
    raise NotImplementedError
    # data = loads(request.body.decode('utf-8'))['data']
    # invitee_email = data['invitee_email']
    # subject = data['subject']
    # message = data['message']
    # sender = data.get('email', user_email)
    # recipients = LIST_OF_EMAIL_RECIPIENTS
    # text = "You're invited to the Cannlytics Console"
    # text += '\n\n{0}'.format(message)
    # send_mail(
    #     subject=subject.strip(),
    #     message=text,
    #     from_email=sender,
    #     recipient_list=LIST_OF_EMAIL_RECIPIENTS + [invitee_email, user_email],
    #     fail_silently=False,
    # )
    # return JsonResponse({'success': True}, status=204)


def send_results(request, *args, **argv): #pylint: disable=unused-argument
    """Email certificates from the console to the specified recipients."""
    try:
        claims = authenticate_request(request)
        uid = claims['uid']
    except KeyError:
        return JsonResponse({'success': False, 'message': 'Unauthorized.'}, status=401)
    
    # FIXME: Ensure user can only send results to people who
    # submitted samples with them.
    raise NotImplementedError
    # data = loads(request.body.decode('utf-8'))['data']
    # name = data['name']
    # subject = data['subject']
    # message = data['message']
    # sender = data['email']
    # recipients = LIST_OF_EMAIL_RECIPIENTS
    # if not sender:
    #     sender = DEFAULT_FROM_EMAIL
    # text = 'Laboratory results attached.'
    # text += '\n\n{0}'.format(message)
    # if name is not None:
    #     text += '\n\nFrom,\n' + str(name)
    # send_mail(
    #     subject=subject.strip(),
    #     message=text,
    #     from_email=sender,
    #     recipient_list=recipients,
    #     fail_silently=False,
    # )
    # return JsonResponse({'success': True}, status=204)


def send_message(request, *args, **argv): #pylint: disable=unused-argument
    """Send a message from the console to the Cannlytics admin with email."""
    try:
        claims = authenticate_request(request)
        uid = claims['uid']
    except KeyError:
        return JsonResponse({'success': False, 'message': 'Unauthorized.'}, status=401)
    user_email = claims['email']
    data = loads(request.body.decode('utf-8'))['data']
    name = data.get('name')
    subject = data.get('subject', 'New Cannlytics Console Message')
    message = data['message']
    sender = data.get('email', 'bot@cannlytics.com')
    text = 'Message from the Cannlytics Console:\n\n'
    text += '{}\n\nUser: {}\nUser Email: {}'.format(message, uid, user_email)
    if name is not None:
        text += '\n\nFrom,\n' + str(name)
    send_mail(
        subject=subject.strip(),
        message=text,
        from_email=sender,
        recipient_list=LIST_OF_EMAIL_RECIPIENTS,
        fail_silently=False,
    )
    return JsonResponse({'success': True}, status=204)
