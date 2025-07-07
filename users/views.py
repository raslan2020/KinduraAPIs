from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from .models import User
from .serializers import (
    UserSignupSerializer, UserLoginSerializer, 
    UserProfileSerializer, UserTokenSerializer, UserJSONUploadSerializer
)
from utils.response_utils import success_response, error_response
from utils.authentication import create_user_token, SimpleTokenAuthentication
from rest_framework.parsers import MultiPartParser, FormParser
from .tasks import start_background_processing


class UserViewSet(viewsets.ViewSet):
    """
    ViewSet for user authentication and profile management
    """
    authentication_classes = [SimpleTokenAuthentication]
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def signup(self, request):
        """
        User signup endpoint
        """
        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user_token = create_user_token(user)
            token_serializer = UserTokenSerializer(user_token)
            
            return success_response({
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'username': user.username
                },
                'token': token_serializer.data['token']
            }, "User registered successfully", status.HTTP_201_CREATED)
        else:
            return error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        """
        User login endpoint
        """
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            user_token = create_user_token(user)
            token_serializer = UserTokenSerializer(user_token)
            
            return success_response({
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'username': user.username
                },
                'token': token_serializer.data['token']
            }, "Login successful")
        else:
            return error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get', 'put'], permission_classes=[IsAuthenticated])
    def profile(self, request):
        """
        Get and update user profile
        """
        if request.method == 'GET':
            serializer = UserProfileSerializer(request.user)
            return success_response(serializer.data)
        
        elif request.method == 'PUT':
            serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return success_response(serializer.data, "Profile updated successfully")
            else:
                return error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        """
        User logout endpoint
        """
        # Deactivate current token
        token = request.auth
        if token:
            from .models import UserToken
            UserToken.objects.filter(token=token).update(is_active=False)
        
        return success_response(message="Logout successful")

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated], parser_classes=[MultiPartParser, FormParser])
    def upload_json(self, request):
        """
        Upload a JSON file and store its content for the authenticated user
        Processing happens asynchronously in the background
        """
        serializer = UserJSONUploadSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            json_upload = serializer.save()
            
            # Start background processing
            start_background_processing(json_upload.id)
            
            return success_response({
                'id': json_upload.id,
                'status': json_upload.status,
                'uploaded_at': json_upload.uploaded_at,
                'message': 'JSON uploaded successfully. Processing started in background.'
            }, "JSON uploaded successfully", status.HTTP_201_CREATED)
        return error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def json_status(self, request, pk=None):
        """
        Check the processing status of a JSON upload
        """
        try:
            from .models import UserJSON
            json_upload = UserJSON.objects.get(id=pk, user=request.user)
            
            response_data = {
                'id': json_upload.id,
                'status': json_upload.status,
                'uploaded_at': json_upload.uploaded_at,
            }
            
            if json_upload.status == 'completed':
                response_data['summarize_patient_report'] = json_upload.summarize_patient_report
            elif json_upload.status == 'failed':
                response_data['error_message'] = json_upload.error_message
            
            return success_response(response_data)
            
        except UserJSON.DoesNotExist:
            return error_response("JSON upload not found", status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def json_uploads(self, request):
        """
        Get all JSON uploads for the authenticated user
        """
        from .models import UserJSON
        json_uploads = UserJSON.objects.filter(user=request.user).order_by('-uploaded_at')
        
        uploads_data = []
        for upload in json_uploads:
            upload_data = {
                'id': upload.id,
                'status': upload.status,
                'uploaded_at': upload.uploaded_at,
            }
            
            if upload.status == 'completed':
                upload_data['summarize_patient_report'] = upload.summarize_patient_report
            elif upload.status == 'failed':
                upload_data['error_message'] = upload.error_message
                
            uploads_data.append(upload_data)
        
        return success_response(uploads_data)
