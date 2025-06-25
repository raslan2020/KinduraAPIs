from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from .models import Medicine
from .serializers import MedicineSerializer
from utils.response_utils import success_response, error_response
from utils.authentication import SimpleTokenAuthentication


class MedicineViewSet(viewsets.ViewSet):
    """
    ViewSet for medicine management
    """
    authentication_classes = [SimpleTokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Medicine.objects.filter(user=self.request.user, is_active=True)
    
    def list(self, request):
        """
        List all medicines for the authenticated user
        """
        try:
            medicines = self.get_queryset()
            serializer = MedicineSerializer(medicines, many=True)
            return success_response(serializer.data)
        except Exception as e:
            return error_response(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def create(self, request):
        """
        Create a new medicine
        """
        try:
            serializer = MedicineSerializer(data=request.data)
            if serializer.is_valid():
                medicine = serializer.save(user=request.user)
                return success_response(
                    MedicineSerializer(medicine).data,
                    "Medicine created successfully",
                    status.HTTP_201_CREATED
                )
            else:
                return error_response(str(serializer.errors), status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return error_response(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def retrieve(self, request, pk=None):
        """
        Retrieve a specific medicine
        """
        try:
            medicine = self.get_queryset().get(pk=pk)
            serializer = MedicineSerializer(medicine)
            return success_response(serializer.data)
        except Medicine.DoesNotExist:
            return error_response("Medicine not found", status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return error_response(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update(self, request, pk=None):
        """
        Update a specific medicine
        """
        try:
            medicine = self.get_queryset().get(pk=pk)
            serializer = MedicineSerializer(medicine, data=request.data, partial=True)
            if serializer.is_valid():
                updated_medicine = serializer.save()
                return success_response(
                    MedicineSerializer(updated_medicine).data,
                    "Medicine updated successfully"
                )
            else:
                return error_response(str(serializer.errors), status.HTTP_400_BAD_REQUEST)
        except Medicine.DoesNotExist:
            return error_response("Medicine not found", status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return error_response(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def destroy(self, request, pk=None):
        """
        Soft delete a medicine (set is_active to False)
        """
        try:
            medicine = self.get_queryset().get(pk=pk)
            medicine.is_active = False
            medicine.save()
            return success_response(message="Medicine deleted successfully")
        except Medicine.DoesNotExist:
            return error_response("Medicine not found", status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return error_response(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)
