from rest_framework import routers
from django.urls import path, include
from .views import VehicleViewSet

router = routers.DefaultRouter()
router.register('', VehicleViewSet)

urlpatterns = [
    path('', include(router.urls))
]
