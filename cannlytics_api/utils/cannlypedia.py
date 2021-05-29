from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def scholars(request, format=None):
    """Get information about scholars."""

    if request.method == 'GET':
        author = request.query_params.get('q', None)
        if author:
            from scholarly import scholarly
            search_query = scholarly.search_author(author)
            author_source = next(search_query)
            author_data = {
                'author': author,
                'affiliation': author_source['affiliation'],
                'cited_by': author_source['citedby'],
                'email_domain': author_source['email_domain'],
                'interests': author_source['interests'],
                'photo_url': author_source['url_picture'],
            } 
            return Response(author_data, content_type="application/json")
        
        # Return an error if no author is specified.
        error_message = 'Author not found in request. Specify ?q={url_encoded_author_name}'
        return Response(
            { "error": error_message},
            content_type="application/json",
            status=status.HTTP_400_BAD_REQUEST
        )
