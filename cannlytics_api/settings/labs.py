from datetime import datetime
from django.template.defaultfilters import slugify
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from utils.firebase import get_collection, get_document, update_document
from .auth import authenticate


@api_view(['GET'])
def lab(request, format=None):
    """Get or update information about a lab."""

    # Query labs.
    if request.method == 'GET':
        limit = request.query_params.get("limit", None)
        order_by = request.query_params.get("order_by", "state")
        # TODO: Get any filters from dict(request.query_params)
        labs = get_collection('labs', order_by=order_by, limit=limit, filters=[])
        return Response({ "data": labs}, content_type="application/json")


@api_view(['GET', 'POST'])
def labs(request, format=None):
    """Get or update information about labs."""

    # Query labs.
    if request.method == 'GET':
        limit = request.query_params.get("limit", None)
        order_by = request.query_params.get("order_by", "state")
        # TODO: Get any filters from dict(request.query_params)
        labs = get_collection('labs', order_by=order_by, limit=limit, filters=[])
        return Response({ "data": labs}, content_type="application/json")

    # Update a lab given a valid Firebase token.
    elif request.method == 'POST':

        # Check token.
        try:
            claims = authenticate(request)
        except:
            return Response({"error": "Could not authenticate."}, status=status.HTTP_400_BAD_REQUEST)

        # Get the posted lab data.
        lab = request.data
        org_id = lab["id"]
        lab["slug"] = slugify(lab["name"])

        # TODO: Handle adding labs.
        # Create uuid, latitude, and longitude, other fields?

        # Determine any changes.
        existing_data = get_document(f"labs/{org_id}")
        changes = []
        for key, after in lab:
            before = existing_data[key]
            if before != after:
                changes.append({"key": key, "before": before, "after": after})
        
        # Get a timestamp.
        timestamp = datetime.now().isoformat()
        lab["updated_at"] = timestamp

        # Create a change log.
        log_entry = {
            "action": "Updated lab data.",
            "type": "change",
            "created_at": lab["updated_at"],
            "user": claims["uid"],
            "user_name": claims["display_name"],
            "user_email": claims["email"],
            "photo_url": claims["photo_url"],
            "changes": changes,
        }
        update_document(f"labs/{org_id}/logs/{timestamp}", log_entry)

        # Update the lab.
        update_document(f"labs/{org_id}", lab)

        return Response(log_entry, status=status.HTTP_201_CREATED)


@api_view(['GET', 'POST'])
def lab_logs(request, org_id, format=None):
    """Get or create lab logs."""

    if request.method == 'GET':
        data = get_collection(f"labs/{org_id}/logs")
        return Response({ "data": data}, content_type="application/json")
    
    elif request.method == 'POST':
        # TODO: Create a log.
        return Response({ "data": "Under construction"}, content_type="application/json")



@api_view(['GET', 'POST'])
def lab_analyses(request, org_id, format=None):
    """
    Get or update (TODO) lab analyses.
    """

    if request.method == 'GET':
        data = get_collection(f"labs/{org_id}/analyses")
        return Response({ "data": data}, content_type="application/json")
    
    elif request.method == 'POST':
        # TODO: Create an analysis.
        return Response({ "data": "Under construction"}, content_type="application/json")

