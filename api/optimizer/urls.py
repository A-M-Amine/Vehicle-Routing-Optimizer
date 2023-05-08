from rest_framework import routers
from django.urls import path, include
from .views import OptimizerViewSet, DeliveryViewSet

router = routers.DefaultRouter()
router.register('optimizer', OptimizerViewSet, basename='optimizer')
router.register('delivery', DeliveryViewSet, basename='delivery')

urlpatterns = [
    path('', include(router.urls)),
    path('optimizer/<int:optimizer_pk>/delivery/', DeliveryViewSet.as_view({'get': 'list', 'put': 'update'}),
         name='optimizer-delivery-list'),
    path('optimizer/<int:optimizer_pk>/delivery/<int:pk>/', DeliveryViewSet.as_view({'get': 'retrieve'}),
         name='optimizer-delivery-detail'),
]
