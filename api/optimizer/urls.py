from rest_framework import routers
from django.urls import path, include
from .views import OptimizerViewSet, DeliveryViewSet

router = routers.DefaultRouter()
router.register('optimizer', OptimizerViewSet, basename='optimizer')
router.register('delivery', DeliveryViewSet, basename='delivery')

urlpatterns = [
    path('', include(router.urls))
]
