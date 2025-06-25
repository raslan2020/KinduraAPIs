import os
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from livekit import api
import asyncio
from utils.response_utils import success_response, error_response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_token(request):
    """
    Generate LiveKit access token for authenticated user
    """
    try:
        data = request.data
        
        # Validate required fields
        required_fields = ['identity', 'name', 'room', 'user_data']
        if not all(field in data for field in required_fields):
            return error_response(
                "Missing one or more required fields: identity, name, room, user_data", 
                status.HTTP_400_BAD_REQUEST
            )

        # Generate LiveKit token
        token = api.AccessToken(
            os.getenv('LIVEKIT_API_KEY'),
            os.getenv('LIVEKIT_API_SECRET')
        ).with_identity(data['identity']) \
         .with_name(data['name']) \
         .with_metadata(json.dumps(data['user_data'])) \
         .with_grants(api.VideoGrants(
             room_join=True,
             room=data['room']
         ))

        return success_response({'token': token.to_jwt()})

    except Exception as e:
        return error_response(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_room(request):
    """
    Delete a LiveKit room
    """
    try:
        data = request.data
        if not data or 'room' not in data:
            return error_response("Missing room field", status.HTTP_400_BAD_REQUEST)

        room_name = data['room']

        # Call the async delete method inside event loop
        asyncio.run(
            api.LiveKitAPI(
                os.getenv('LIVEKIT_URL'), 
                os.getenv('LIVEKIT_API_KEY'), 
                os.getenv('LIVEKIT_API_SECRET')
            ).room.delete_room(
                api.DeleteRoomRequest(room=room_name)
            )
        )
        
        return success_response(
            f'Room "{room_name}" deleted successfully'
        )

    except Exception as e:
        return error_response(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR) 