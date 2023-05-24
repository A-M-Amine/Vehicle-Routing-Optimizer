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

        if data['vehicle_routes'] == {}:
            data['vehicle_routes'] = []
        
        return data
