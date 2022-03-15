"""
Email Views | Cannlytics Website
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 8/22/2021
Updated: 1/14/2022
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>
"""
# Standard imports.
import json

# External imports
from django.core.mail import send_mail
from django.http import JsonResponse

# Internal imports
from cannlytics.auth.auth import authenticate_request
from cannlytics.firebase import create_log
from website.settings import LIST_OF_EMAIL_RECIPIENTS


def send_message(request):
    """Send a message from the website to the Cannlytics admin through email.
    The user must provide an `email`, `subject`, and `message` in their POST.
    """
    try:
        request.POST['math_input'] == request.POST['math_total']
    except KeyError:
        return JsonResponse({'success': False, 'message': 'Bugger off.'}, status=401)
    claims = authenticate_request(request)
    uid = claims.get('uid', 'User not signed in.')
    user_email = claims.get('email', 'Unknown')
    name = request.POST.get('name', claims.get('name', 'Unknown'))
    try:
        subject = request.POST['subject']
        message = request.POST['message']
        sender = request.POST['email']
    except:
        message = 'An `email`, `subject`, and `message` are required.'
        return JsonResponse({'success': False, 'message': message}, status=400)
    recipients = LIST_OF_EMAIL_RECIPIENTS
    template = 'New message from the Cannlytics website:' \
               '\n\n{0}\n\nUser: {0}\nUser Email: {0}\n\nFrom,\n{0}'
    text = template.format(message, uid, user_email, name)
    send_mail(
        subject=subject.strip(),
        message=text,
        from_email=sender,
        recipient_list=recipients,
        fail_silently=False,
    )
    create_log(
        ref='logs/website/email',
        claims=claims,
        action=f'User ({user_email}) sent the staff an email.',
        log_type='email',
        key='send_message',
        changes={'message': message, 'name': name, 'subject': subject, 'uid': uid},
    )
    response = {'success': True, 'message': 'Message sent to the Cannlytics staff.'}
    return JsonResponse(response)


def suggest_edit(request):
    """Send a data edit suggestion to the staff. The user must be signed into 
    their account to suggest an edit."""
    claims = authenticate_request(request)
    try:
        uid = claims['uid']
        user_email = claims['email']
        name = claims.get('name', 'Unknown')
    except KeyError:
        response = {'success': False, 'message': 'Authentication required for suggestion.'}
        return JsonResponse(response)
    subject = request.POST.get('subject', 'Cannlytics Website Data Edit Recommendation')
    recipients = LIST_OF_EMAIL_RECIPIENTS
    suggestion = request.POST['suggestion']
    message = json.dumps(suggestion, sort_keys=True, indent=4)
    template = 'New data edit recommendation from the Cannlytics website:' \
               '\n\n{0}\n\nUser: {0}\nUser Email: {0}\n\nFrom,\n{0}'
    text = template.format(message, uid, user_email, name)
    send_mail(
        subject=subject.strip(),
        message=text,
        from_email=user_email,
        recipient_list=recipients,
        fail_silently=False,
    )
    create_log(
        ref='logs/website/suggestions',
        claims=claims,
        action=f'User ({user_email}) suggested a data edit to the staff in an email.',
        log_type='email',
        key='suggest_edit',
        changes={'message': message, 'name': name, 'subject': subject, 'uid': uid},
    )
    response = {'success': True, 'message': 'Data edit suggestion sent to the staff.'}
    return JsonResponse(response)
