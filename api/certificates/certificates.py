"""
Certificates Views | Cannlytics API
Created: 7/19/2021
Updated: 7/19/2021

API to interface with certificates of analysis.
"""
# pylint:disable=line-too-long

# External imports
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Internal imports
from api.auth.auth import authenticate_request
from api.api import get_objects, update_object, delete_object


@api_view(['POST'])
def generate_coas(request):
    """Generate certificates of analysis."""
    return NotImplementedError


@api_view(['POST'])
def review_coas(request):
    """Review certificates of analysis."""
    return NotImplementedError


@api_view(['POST'])
def approve_coas(request):
    """Approve certificates of analysis."""
    return NotImplementedError
