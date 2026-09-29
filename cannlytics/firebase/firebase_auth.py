"""
Firebase Authentication | Cannlytics Firebase Module
Copyright (c) 2021-2026 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 2/7/2021
Updated: 9/28/2026
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description: Firebase Auth user management — create users, manage
custom claims, generate tokens and session cookies, and verify
authentication credentials.
"""
# Standard imports:
from __future__ import annotations
import logging
from datetime import timedelta
from typing import Any

# External imports:
from firebase_admin import auth
from firebase_admin.auth import EmailAlreadyExistsError

# Module logger. Never log a user's e-mail address or password.
logger = logging.getLogger(__name__)

# Internal imports:
from .core import create_id
from cannlytics.utils import get_random_string


# === User Management ===

def create_user(name: str, email: str) -> tuple[Any | None, str | None]:
    """Create a Firebase Auth user with a generated password.

    No profile photo is set: choosing one is the application's business.
    (Before 1.0.5 this set ``https://robohash.org/<email>``, which put
    the user's e-mail address in a third-party URL requested every time
    the avatar was shown.)

    Args:
        name: Display name for the user.
        email: The user's email address.

    Returns:
        A tuple of ``(UserRecord, password)`` on success, or
        ``(None, None)`` if the e-mail is already in use or the user
        could not be created (that failure is logged, without the
        address).
    """
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$-_'
    password = get_random_string(42, chars)
    try:
        user = auth.create_user(
            uid=create_id(),
            email=email,
            email_verified=False,
            password=password,
            display_name=name,
            disabled=False,
        )
    except EmailAlreadyExistsError:
        return None, None
    except Exception as error:
        logger.error('Could not create a Firebase Auth user: %s', type(error).__name__)
        return None, None
    return user, password


def get_user(name: str) -> Any | None:
    """Get a user by user ID, email, or phone number.

    Attempts lookup in order: UID, email, phone number.

    Args:
        name: A user ID, email address, or phone number.

    Returns:
        A Firebase ``UserRecord``, or ``None`` if not found.
    """
    user = None
    try:
        user = auth.get_user(name)
    except Exception:
        pass
    if user is None:
        try:
            user = auth.get_user_by_email(name)
        except Exception:
            pass
    if user is None:
        try:
            user = auth.get_user_by_phone_number(name)
        except Exception:
            pass
    return user


def get_users() -> list:
    """Get all Firebase Auth users.

    Returns:
        A list of all ``UserRecord`` objects.
    """
    users = []
    for user in auth.list_users().iterate_all():
        users.append(user)
    return users


def update_user(existing_user: Any, data: dict) -> Any:
    """Update a user's profile fields.

    Supported fields: ``email``, ``phone_number``,
    ``email_verified``, ``display_name``, ``photo_url``,
    ``disabled``.

    Args:
        existing_user: A Firebase ``UserRecord`` object.
        data: Dictionary of fields to update.

    Returns:
        The updated ``UserRecord``.
    """
    values = {}
    fields = [
        'email', 'phone_number', 'email_verified',
        'display_name', 'photo_url', 'disabled',
    ]
    for field in fields:
        new_value = data.get(field)
        if new_value:
            values[field] = new_value
        else:
            values[field] = getattr(existing_user, field)
    return auth.update_user(
        existing_user.uid,
        email=values['email'],
        phone_number=values['phone_number'],
        email_verified=values['email_verified'],
        display_name=values['display_name'],
        photo_url=values['photo_url'],
        disabled=values['disabled'],
    )


def delete_user(uid: str):
    """Delete a user from Firebase Auth.

    Args:
        uid: The user's Firebase UID.
    """
    auth.delete_user(uid)


def generate_password_reset_link(email: str) -> str:
    """Generate a password reset link for a user.

    Args:
        email: The user's email address.

    Returns:
        A password reset URL.
    """
    return auth.generate_password_reset_link(email)


# === Custom Claims ===

def create_custom_claims(
        uid: str,
        email: str | None = None,
        claims: dict | None = None,
    ) -> None:
    """Set custom claims for a user.

    Custom claims propagate to the user's ID token the next
    time a new one is issued.

    Args:
        uid: The user's Firebase UID.
        email: Optionally look up UID by email instead.
        claims: A dictionary of custom claims to set.
    """
    if email:
        user = auth.get_user_by_email(email)
        uid = user.uid
    auth.set_custom_user_claims(uid, claims)


def update_custom_claims(
        uid: str,
        email: str | None = None,
        claims: dict | None = None,
    ) -> dict:
    """Merge new custom claims with existing claims for a user.

    Args:
        uid: The user's Firebase UID.
        email: Optionally look up UID by email instead.
        claims: A dictionary of claims to merge.

    Returns:
        The merged claims dictionary.
    """
    if email:
        user = auth.get_user_by_email(email)
        uid = user.uid
    existing_claims = get_custom_claims(uid)
    if not existing_claims:
        existing_claims = {}
    new_claims = {**existing_claims, **claims}
    auth.set_custom_user_claims(uid, new_claims)
    return new_claims


def get_custom_claims(name: str) -> dict | None:
    """Get custom claims for a user.

    Args:
        name: A user ID or email address.

    Returns:
        A dictionary of the user's custom claims, or ``None``.
    """
    user = get_user(name)
    return user.custom_claims


# === Tokens & Sessions ===

def create_custom_token(
        uid: str = '',
        email: str | None = None,
        claims: dict | None = None,
    ) -> bytes:
    """Create a custom authentication token.

    Custom tokens expire after one hour.

    Args:
        uid: The user's Firebase UID.
        email: Optionally look up UID by email instead.
        claims: Optional claims to embed in the token.

    Returns:
        A signed custom token as bytes.
    """
    if email:
        user = auth.get_user_by_email(email)
        uid = user.uid
    return auth.create_custom_token(uid, claims)


def create_session_cookie(
        id_token: str,
        expires_in: timedelta | None = None,
    ) -> bytes:
    """Create a session cookie from a Firebase ID token.

    Args:
        id_token: A user's ID token from the client.
        expires_in: Cookie lifetime (default: 7 days).

    Returns:
        A session cookie as bytes.
    """
    if expires_in is None:
        expires_in = timedelta(days=7)
    return auth.create_session_cookie(id_token, expires_in=expires_in)


def revoke_refresh_tokens(token: str):
    """Revoke all refresh tokens for a user.

    Args:
        token: The user's refresh token or UID.
    """
    auth.revoke_refresh_tokens(token)


def verify_token(token: str) -> dict:
    """Verify a Firebase ID token.

    Args:
        token: The ID token to verify.

    Returns:
        The decoded token claims as a dictionary.
    """
    return auth.verify_id_token(token)


def verify_session_cookie(
        session_cookie: str,
        check_revoked: bool = True,
        app: Any | None = None,
    ) -> dict:
    """Verify a session cookie.

    Args:
        session_cookie: The session cookie string.
        check_revoked: Whether to check if the cookie is revoked.
        app: Optional Firebase App instance.

    Returns:
        The decoded session claims as a dictionary.
    """
    return auth.verify_session_cookie(
        session_cookie,
        check_revoked=check_revoked,
        app=app,
    )