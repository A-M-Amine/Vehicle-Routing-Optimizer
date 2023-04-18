from rest_framework import routers
from django.urls import path, include
from .views import OptimizerViewSet

router = routers.DefaultRouter()
router.register('', OptimizerViewSet, basename='optimizer')


urlpatterns = [
    path('', include(router.urls))
]

