import os
from livekit import api
from flask import Flask, request, jsonify
from livekit.api import DeleteRoomRequest
import asyncio
app = Flask(__name__)

@app.route('/getToken', methods=['POST'])
def get_token():
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['identity', 'name', 'room']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing one or more required fields: identity, name, room'}), 400

    try:
        token = api.AccessToken(
            os.getenv('LIVEKIT_API_KEY'),
            os.getenv('LIVEKIT_API_SECRET')
        ).with_identity(data['identity']) \
         .with_name(data['name']) \
         .with_grants(api.VideoGrants(
             room_join=True,
             room=data['room']
         ))

        return jsonify({'token': token.to_jwt()}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/delete-room', methods=['POST'])
def delete_room():
    data = request.get_json()
    if not data or 'room' not in data:
        return jsonify({'error': 'Missing room field'}), 400

    room_name = data['room']

    try:
        # Call the async delete method inside event loop
        asyncio.run(api.LiveKitAPI(os.getenv('LIVEKIT_URL'), os.getenv('LIVEKIT_API_KEY'), os.getenv('LIVEKIT_API_SECRET')).room.delete_room(DeleteRoomRequest(room=room_name)))
        return jsonify({'message': f'Room "{room_name}" deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)