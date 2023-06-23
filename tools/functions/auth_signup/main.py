"""
Authentication Sign Up | Cannlytics
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 6/23/2023
Updated: 6/23/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Populate a user's account with trial tokens when they sign up.

"""
# External imports.
from cannlytics import firebase
from firebase_admin import initialize_app


def auth_signup(data, context):
    """Triggered by creation or deletion of a Firebase Auth user object.
    Args:
           data (dict): The event payload.
           context (google.cloud.functions.Context): Metadata for the event.
    """
    uid = data['uid']
    print('Function triggered by creation/deletion of user: %s' % uid)
    print('Created at: %s' % data['metadata']['createdAt'])

    if 'email' in data:
        print('Email: %s' % data['email'])

    # Add 10 trial tokens to the user's account.
    if data['metadata']['createdAt'] == data['metadata']['lastSignedInAt']:
        print('User signed up for the first time.')
        try:
            initialize_app()
        except ValueError:
            pass
        entry = {'tokens': 10, 'support': 'free'}
        firebase.update_document(f'subscribers/{uid}', entry)
        print('Added 10 tokens for user: %s' % uid)

    # TODO: Send a welcome email.


    # TODO: Send an email to the Cannlytics admin.


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
