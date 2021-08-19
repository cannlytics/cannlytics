# -*- coding: utf-8 -*-
"""
setup.py | Cannlytics

Author: Keegan Skeate <keegan@cannlytics.com>
Contact: <keegan@cannlytics.com>
Created: 1/21/2021
Updated: 6/21/2021
License: MIT
"""
import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='cannlytics',
    version='0.0.8',
    author='Cannlytics',
    author_email='contact@cannlytics.com',
    description='Cannlytics is simple, easy-to-use, end-to-end cannabis analytics software designed to make your data and information accessible.',
    long_description='Cannlytics makes cannabis analysis **simple** and **easy** through data accessibility. We believe that everyone in the cannabis industry should be able to access rich, valuable data quickly and easily and that you will be better off for it.',
    long_description_content_type='text/markdown',
    url='https://github.com/cannlytics/cannlytics',
    packages=setuptools.find_packages(),
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.8',
    include_package_data=True,
    install_requires=[
        'beautifulsoup4',
        'django',
        'firebase_admin',
        'googlemaps',
        'pandas',
    ],
)
