"""
Title | Project

Author: Keegan Skeate
Contact: <keegan@cannlytics.com>
Created: 
Updated: 
License: MIT License <https://opensource.org/licenses/MIT>
"""

if __name__ == '__main__':

    from django.utils.crypto import get_random_string

    # Generate a secret key for your project.
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    generated_secret_key = get_random_string(50, chars)
    print(generated_secret_key)
