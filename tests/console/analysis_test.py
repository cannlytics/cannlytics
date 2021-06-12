"""
Example Test | Cannlytics Console
Author: Keegan Skeate <keegan@cannlytics.com>
Created: 6/8/2021
Updated: 6/8/2021
Description:

The following is an example a normal unit test for DJango.
Django uses the standard Unittest library. The steps entail:

    1. Import the Post model from the application.
    2. Create a post object with some initial values.
    3. Check that the values match expectations.

You can then run the test case with:

    python manage.py test

Resources:
    https://docs.python.org/3/library/unittest.html
"""

# Standard imports.
import os
import sys

# External imports.
from django.test import TestCase

# Internal imports.
# Import cannlytics locally for testing.
sys.path.insert(0, os.path.abspath('../../'))
from cannlytics.models import Analysis # pylint: disable=no-name-in-module, import-error


class AnalysisModelTestCase(TestCase):
    """A simple test of analysis models."""

    def test_create(self):
        """Test the creation of an analysis model."""
        data = Analysis(public=False)
        self.assertEqual(data.public, False)
