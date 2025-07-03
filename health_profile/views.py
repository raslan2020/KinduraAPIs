from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from .models import HealthProfile
from .serializers import HealthProfileSerializer
from utils.response_utils import success_response, error_response
from utils.authentication import SimpleTokenAuthentication


class HealthProfileViewSet(viewsets.ViewSet):
    """
    ViewSet for health profile management
    """
    authentication_classes = [SimpleTokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return HealthProfile.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get', 'post', 'put'], permission_classes=[IsAuthenticated])
    def profile(self, request):
        """
        Get, create, or update health profile
        """
        if request.method == 'GET':
            try:
                health_profile = self.get_queryset().first()
                if health_profile:
                    serializer = HealthProfileSerializer(health_profile)
                    return success_response(serializer.data)
                else:
                    return error_response("Health profile not found", status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return error_response(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        elif request.method == 'POST':
            try:
                # Check if profile already exists
                existing_profile = self.get_queryset().first()
                if existing_profile:
                    return error_response("Health profile already exists. Use PUT to update.", status.HTTP_400_BAD_REQUEST)
                
                serializer = HealthProfileSerializer(data=request.data)
                if serializer.is_valid():
                    health_profile = serializer.save(user=request.user)
                    return success_response(
                        HealthProfileSerializer(health_profile).data,
                        "Health profile created successfully",
                        status.HTTP_201_CREATED
                    )
                else:
                    return error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return error_response(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        elif request.method == 'PUT':
            try:
                health_profile = self.get_queryset().first()
                
                if health_profile:
                    # Update existing profile
                    serializer = HealthProfileSerializer(health_profile, data=request.data, partial=True)
                    if serializer.is_valid():
                        updated_profile = serializer.save()
                        return success_response(
                            HealthProfileSerializer(updated_profile).data,
                            "Health profile updated successfully"
                        )
                    else:
                        return error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)
                else:
                    # Create new profile if it doesn't exist
                    serializer = HealthProfileSerializer(data=request.data)
                    if serializer.is_valid():
                        health_profile = serializer.save(user=request.user)
                        return success_response(
                            HealthProfileSerializer(health_profile).data,
                            "Health profile created successfully",
                            status.HTTP_201_CREATED
                        )
                    else:
                        return error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return error_response(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)
