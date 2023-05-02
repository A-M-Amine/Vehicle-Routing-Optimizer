from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from .models import OptimizedRoute
from api.vehicle.serializers import VehicleSerializer
from api.vehicle.models import Vehicle
from api.optimizer.models import Optimizer
from api.optimizer.serializers import OptimizerSerializer


class OptimizedRouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = OptimizedRoute
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        self_optimizer = Optimizer.objects.get(id=data['optimizer'])
        self_opt_serializer = OptimizerSerializer(self_optimizer)
        vehicles = Vehicle.objects.filter(id__in=self_opt_serializer.data['vehicles'])
        serializer = VehicleSerializer(vehicles, many=True)
        data_vehicles = serializer.data
        for index, vehicle in enumerate(data_vehicles):
            data['vehicle_routes'][index]['capacity'] = vehicle['capacity']

        return data
