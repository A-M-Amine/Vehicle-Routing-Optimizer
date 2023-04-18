from rest_framework import routers
from django.urls import path, include
from .views import OptimizedRouteViewSet

router = routers.DefaultRouter()
router.register('', OptimizedRouteViewSet)

urlpatterns = [
    path('', include(router.urls))
]
