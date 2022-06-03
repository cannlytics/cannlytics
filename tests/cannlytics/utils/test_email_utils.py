"""
Test Email Utility Functions
Copyright (c) 2022 Cannlytics

Author: Keegan Skeate <keegan@cannlytics.com>
Created: 5/2/2022
Updated: 5/2/2022
License: MIT License <https://github.com/cannlytics/cannlytics-ai/blob/main/LICENSE>
"""
from cannlytics.utils.email import (
    send_password_reset,
    send_email_newsletter,
    send_email_invitation,
)

# TODO: Test `send_password_reset`.
def test_send_password_reset():
    """Test ..."""
    result = send_password_reset()
    assert


# TODO: Test `send_email_newsletter`.
def test_send_email_newsletter():
    """Test ..."""
    result = send_email_newsletter()
    assert


# TODO: Test `send_email_invitation`.
def test_send_email_invitation():
    """Test ..."""
    result = send_email_invitation()
    assert


if __name__ == '__main__':

    test_send_password_reset()
    test_send_email_newsletter()
    test_send_email_invitation()
