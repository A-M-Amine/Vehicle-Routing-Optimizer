from rest_framework import viewsets
from .serializers import OptimizedRouteSerializer
from .models import OptimizedRoute
from rest_framework.decorators import action
from rest_framework.response import Response
import json


class OptimizedRouteViewSet(viewsets.ModelViewSet):
    queryset = OptimizedRoute.objects.all()
    serializer_class = OptimizedRouteSerializer
