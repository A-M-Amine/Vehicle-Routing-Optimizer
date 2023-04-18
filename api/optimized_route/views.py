from rest_framework import viewsets
from .serializers import OptimizedRouteSerializer
from .models import OptimizedRoute, Vehicle


class OptimizedRouteViewSet(viewsets.ModelViewSet):
    queryset = OptimizedRoute.objects.all()
    serializer_class = OptimizedRouteSerializer



