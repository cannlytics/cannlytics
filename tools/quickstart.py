"""
Title | Project

Author: Keegan Skeate
Contact: <keegan@cannlytics.com>
Created: 
Updated: 
License: MIT License <https://opensource.org/licenses/MIT>
"""

from django.utils.crypto import get_random_string

chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
generated_secret_key = get_random_string(50, chars)
print(generated_secret_key)


def generate_secret_key(env_file_name):
    """Generate a Django secret key.
    Args:
        env_file_name (str): An .env file to write the secret key.
    """
    env_file = open(env_file_name, 'w+')
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    generated_secret_key = get_random_string(50, chars)
    print(generated_secret_key)
    env_file.write('SECRET_KEY = "{}"\n'.format(generated_secret_key))
    env_file.close()


if __name__ == '__main__':

    generate_secret_key('../../.env')
