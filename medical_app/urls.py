"""
URL configuration for medical_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.views import UserViewSet
from health_profile.views import HealthProfileViewSet
from courses.views import CourseViewSet
from medicines.views import MedicineViewSet
from schedules.views import CourseMedicineScheduleViewSet, CourseDayTrackingViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'health-profile', HealthProfileViewSet, basename='health-profile')
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'medicines', MedicineViewSet, basename='medicine')
router.register(r'schedules', CourseMedicineScheduleViewSet, basename='schedule')
router.register(r'tracking', CourseDayTrackingViewSet, basename='tracking')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/livekit/', include('livekit_app.urls')),
]
