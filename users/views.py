from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from .models import User
from .serializers import (
    UserSignupSerializer, UserLoginSerializer, 
    UserProfileSerializer, UserTokenSerializer
)
from utils.response_utils import success_response, error_response
from utils.authentication import create_user_token, SimpleTokenAuthentication


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
