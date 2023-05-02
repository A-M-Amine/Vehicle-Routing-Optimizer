from rest_framework import viewsets
from .serializers import VehicleSerializer
from .models import Vehicle


class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
