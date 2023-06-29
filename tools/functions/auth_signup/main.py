"""
Authentication Sign Up | Cannlytics
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 6/23/2023
Updated: 6/28/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Populate a user's account with trial tokens when they sign up.
    Then send a welcome email to the user and a notification email
    to the admin.

"""
# Standard imports:
import os
import smtplib
from email.mime.text import MIMEText

# External imports:
from cannlytics import firebase
from firebase_admin import initialize_app


def auth_signup(data, context):
    """Triggered by creation or deletion of a Firebase Auth user object.
    Args:
           data (dict): The event payload.
           context (google.cloud.functions.Context): Metadata for the event.
    """
    uid = data['uid']
    created_at = data['metadata']['createdAt']
    print('Function triggered by creation/deletion of user: %s' % uid)
    print('Created at: %s' % created_at)

    # Get the user's email.
    user_email = None
    if 'email' in data:
        user_email = data['email']
        print('Email: %s' % user_email)

    # Add 10 trial tokens to the user's account.
    if created_at == data['metadata']['lastSignedInAt']:
        print('User signed up for the first time.')
        try:
            initialize_app()
        except ValueError:
            pass
        entry = {
            'created_at': created_at,
            'support': 'free',
            'tokens': 10,
            'uid': uid,
            'email': user_email,
        }
        firebase.update_document(f'subscribers/{uid}', entry)
        print('Added 10 tokens for user: %s' % uid)

    # Get email credentials.
    admin_email = os.environ.get('EMAIL_HOST_USER')
    admin_email_password = os.environ.get('EMAIL_HOST_PASSWORD')
    admin_email_host = os.environ.get('EMAIL_HOST')
    admin_email_port = os.environ.get('EMAIL_PORT')

    # Start the email server.
    server = smtplib.SMTP(admin_email_host, admin_email_port)
    server.starttls()
    server.login(admin_email, admin_email_password)

    # Send a welcome email.
    try:
        msg = MIMEText('Welcome to Cannlytics')
        msg['Subject'] = 'Welcome!'
        msg['From'] = admin_email
        msg['To'] = user_email
        html = """
        <html>
        <head>
            <style>
                .serif {
                    font-family: 'Times New Roman', Times, serif;
                }
                .mt-2 {
                    margin-top: 0.5rem;
                }
                a {
                    color: #0d6efd;
                    text-decoration: underline;
                }
            </style>
        </head>
        <body>
            <p>Welcome to Cannlytics,</p>
            <p>Explore subscription plans and find the right plan for you at <a href="https://cannlytics.com/account/subscriptions">https://cannlytics.com/account/subscriptions</a>.</p>
            <p class="mt-2" style="max-width:560px;">
                You can get access to bleeding-edge AI tools to give yourself a competitive edge, including:
                <a href="https://data.cannlytics.com/results">a COA parser</a>,
                <a href="https://data.cannlytics.com/sales">a receipt parser</a>,
                <a href="https://data.cannlytics.com/licenses">licenses data archive</a>, and
                <a href="https://cannlytics.com/api">API access</a>.
            </p>
            <p>As a new user, you have received <strong class="serif">10 free tokens</strong> to try Cannlytics AI.</p>
            <p>Each Cannlytics AI job consumes <strong class="serif">1 token</strong>. Only successful jobs will consume tokens. Your tokens are valid for <strong class="serif">one month</strong> after purchase. You can always purchase more tokens for your account at <a href="https://cannlytics.com/account">https://cannlytics.com/account</a>.</p>
            <p>You can use your tokens to run AI-powered jobs in the app: <a href="https://data.cannlytics.com">https://data.cannlytics.com</a>. Put your AI jobs to good use!</p>
            <p>Thank you for subscribing,<br>The Cannabis Data Science Team</p>
        </body>
        </html>
        """
        part = MIMEText(html, 'html')
        msg.attach(part)
        server.send_message(msg)
        print('Welcome email sent to user: %s' % uid)
    except:
        print('Failed to send welcome email to user: %s' % uid)

    # Send an email to the Cannlytics admin.
    try:
        subject = 'A new user signed up!\n'
        for key, value in entry.items():
            subject += f'\n{key}: {value}'
        msg = MIMEText(f'New user: {uid}')
        msg['Subject'] = subject
        msg['From'] = admin_email
        msg['To'] = admin_email
        server.send_message(msg)
    except:
        print('Failed to send email to admin about new user: %s' % uid)

    # Close the email server.
    server.quit()


# === Test ===
if __name__ == '__main__':

    # Mock authentication sign up.
    data = {
        'uid': 'qXRaz2QQW8RwTlJjpP39c1I8xM03',
        'email': 'help@cannlytics.com',
        'metadata': {
            'createdAt': '2023-04-20T00:00:00.000Z',
            'lastSignedInAt': '2023-04-20T00:00:00.000Z',
        }
    }
    auth_signup(data, {})
