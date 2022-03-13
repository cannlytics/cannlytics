"""
Email Utilities | Cannlytics

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 6/23/2021
Updated: 12/21/2021
License: <https://github.com/cannlytics/cannlytics-engine/blob/main/LICENSE>

Description: Various email tools to make your life simple and easy.
"""
from ..firebase import generate_password_reset_link


def send_password_reset(email):
    """Send a password reset to a user given an email."""
    link = generate_password_reset_link(email)
    # TODO: Implement custom password-reset email.
    return NotImplementedError


def send_email_newsletter():
    """Send an email newsletter to a group of organizations."""
    # TODO: Implement.
    return NotImplementedError


def send_email_invitation():
    """Send an email inviting someone to sign up for Cannlytics."""
    # TODO: Implement.
    return NotImplementedError
