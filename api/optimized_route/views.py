from rest_framework import viewsets
from .serializers import OptimizedRouteSerializer, VehicleSerializer
from .models import OptimizedRoute, Vehicle
from rest_framework.decorators import action
from rest_framework.response import Response
import json


class OptimizedRouteViewSet(viewsets.ModelViewSet):
    queryset = OptimizedRoute.objects.all()
    serializer_class = OptimizedRouteSerializer

    @action(detail=False, methods=['get'], url_path="vehicle-path", url_name="vehicle-path")
    def vehicle_path(self, request):
        vehicle_id = request.query_params.get('key')
        try:
            vehicle_instance = Vehicle.objects.get(vehicle_id=vehicle_id)
        except Vehicle.DoesNotExist:
            return Response({'Error': f'vehicle with id {vehicle_id} does not exist'})

        serialized_vehicle = VehicleSerializer(vehicle_instance)
        return Response(serialized_vehicle.data['path'])
