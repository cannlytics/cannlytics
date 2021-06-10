"""
Organizations API Views | Cannlytics API
Created: 4/25/2021
Updated: 6/10/2021
Description: API to interface with organizations.
"""

# External imports
from json import loads
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Internal imports
from cannlytics.firebase import (
    get_collection,
    get_document,
    create_id,
    update_document,
)
from api.auth import auth #pylint: disable=import-error


@api_view(['GET', 'POST'])
def organizations(request, format=None, org_id=None):
    """Get, create, or update organizations.
    E.g.
        ```
        organization = {
                'owner': [],
                'name': '',
                'license': '',
                'type': '',
                'team': [],
                'support': '',
            }
        ```
    """

    print('Requested org:', org_id)

    # claims = auth.authenticate_request(request)
    claims = auth.verify_session(request)
    uid = claims['uid']
    print('User:', uid)

    # Get organization(s).
    if request.method == 'GET':

        # Get org_id parameter
        if org_id:
            print('Query organizations by ID:', org_id)
            organization = get_document(f'organizations/{org_id}')
            if not organization:
                message = 'No organization exists with the given ID.'
                return Response({'error': True, 'message': message}, status=404)
            elif organization['public']:
                return Response(organization, content_type='application/json')
            elif uid not in organization['team']:
                message = 'This is a private organization and you are not a team member. Request to join before continuing.'
                return Response({'error': True, 'message': message}, status=400)
            else:
                return Response(organization, content_type='application/json')

        # TODO: Get query parameters.
        keyword = request.query_params.get('name')
        print('Query by name:', keyword)
        query = {'key': 'name', 'operation': '==', 'value': keyword}
        organizations = get_collection('organizations', filters=[query])

        # TODO: Check if user is in organization's team, otherwise,
        # only return publically available information.

        # TODO: Try to get the organization (facility) from Metrc.
        # facilities = track.get_facilities()

        return Response(organizations, content_type='application/json')

    # Create or update an organization.
    elif request.method == 'POST':

        # Get the posted data.
        organization = {}
        data = loads(request.body.decode('utf-8'))
        org_id = data.get('uid')
        if org_id:

            # TODO: If a user has org_id in their team claims,
            # then they can perform team actions.

            # Return an error if the organization already exists
            # and the user is not part of the organization's team.
            organization = get_document(f'organizations/{org_id}')
            if not organization:
                message = 'No organization exists for the given ID.'
                return Response({'error': True, 'message': message}, status=400)
            if uid not in organization['team']:
                message = 'You are not a team member of this organization. Request to join before continuing.'
                return Response({'error': True, 'message': message}, status=400)

            # If an organization already exists, then only the owner
            # can edit the organization's team.
            if uid != organization['owner']:
                data['team'] = organization['team']

        # Create organization if it doesn't exist
        # All organizations have a unique `org_id`.
        else:
            organization['id'] = create_id()
            organization['team'] = [uid]

        # Create or update the organization in Firestore.
        entry = {**data, **organization}
        update_document(f'users/{uid}', entry)

        # TODO: On organization creation, the creating user get custom claims.
        # owner: [org_id, ...]

        # TODO:  Owners can add other users to the team and
        # the receiving user then gets the claims.
        # team: [org_id, ...]
        # team: [org_id, ...]        

        # Each organization can have multiple licenses.

        # TODO: Create activity log.
        # changes = [post_data]
        # create_log(f'organization/{uid}/logs', claims, 'Updated organization data.', 'organizations', 'organization_data', changes)

        return Response(organization, content_type='application/json')

    elif request.method == 'DELETE':

        # TODO: Only user's with org_id in owner claim can delete the organization.

        return Response({'error': 'not_implemented'}, content_type='application/json')


    # TODO: Implement organization actions:

    # def confirm_join_organization():
    #     """Confirm a user's request to join an organization."""
    #     return NotImplementedError


    # def decline_join_organization():
    #     """Decline a user's request to join an organization."""
    #     return NotImplementedError


    # def join_organization(request):
    #     """Send the owner of an organization a request for a user to join."""

    #     # Identify the user.
    #     claims = auth.authenticate(request)
    #     uid = claims['uid']
    #     user_email = claims['email']
    #     post_data = loads(request.body.decode('utf-8'))
    #     organization = post_data.get('organization')

    #     # Return an error if the organization doesn't exist.
    #     query = {'key': 'organization', 'operation': '==', 'value': organization}
    #     organizations = get_collection('organizations', filters=[query])
    #     if not organizations:
    #         message = 'Organization does not exist. Please check the organization name and try again.'
    #         return Response({'success': False, 'message': message}, status=400)

    #     # Send the owner an email requesting to add the user to the organization's team.
    #     org_email = organizations[0]['email']
    #     text = f"A user with the email address {user_email} would like to join your organization, \
    #         {organization}. Do you want to add this user to your organization's team? Please \
    #         reply YES or NO to confirm."
    #     paragraphs = []
    #     # TODO: Generate confirm, decline, and unsubscribe links with HMACs from user's uid and owner's uid.
    #     user_hmac = ''
    #     owner_hmac = ''
    #     # Optional: Find new home's for endpoints in api and cannlytics_website
    #     confirm_link = f'https://console.cannlytics.com/api/organizations/confirm?hash={owner_hmac}&member={user_hmac}'
    #     decline_link = f'https://console.cannlytics.com/api/organizations/decline?hash={owner_hmac}&member={user_hmac}'
    #     unsubscribe_link = f'https://console.cannlytics.com/api/unsubscribe?hash={owner_hmac}'
    #     html_message = render_to_string('templates/console/emails/action_email_template.html', {
    #         'recipient': org_email,
    #         'paragraphs': paragraphs,
    #         'primary_action': 'Confirm',
    #         'primary_link': confirm_link,
    #         'secondary_action': 'Decline',
    #         'secondary_link': decline_link,
    #         'unsubscribe_link': unsubscribe_link,
    #     })

    #     # TODO: Skip sending email if owner is unsubscribed.
    #     send_mail(
    #         subject="Request to join your organization's team.",
    #         message=text,
    #         from_email=DEFAULT_FROM_EMAIL,
    #         recipient_list=LIST_OF_EMAIL_RECIPIENTS,
    #         fail_silently=False,
    #         html_message=html_message
    #     )

    #     # Create activity logs.
    #     create_log(f'users/{uid}/logs', claims, 'Requested to join an organization.', 'users', 'user_data', [post_data])
    #     create_log(f'organization/{uid}/logs', claims, 'Request from a user to join the organization.', 'organizations', 'organization_data', [post_data])

    #     message = f'Request to join {organization} sent to the owner.'
    #     return Response({'success': True, 'message': message}, content_type='application/json')


    # @api_view(['GET', 'POST'])
    # def staff():
    #     """Get, create, or update information about an organization's staff."""
    #     return NotImplementedError
