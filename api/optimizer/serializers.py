from rest_framework import serializers
from .models import Optimizer
from api.optimized_route.serializers import OptimizedRouteSerializer
from api.optimized_route.models import OptimizedRoute
from .validators import validate_locations_value, validate_depot_value


class OptimizerSerializer(serializers.ModelSerializer):
    optimizedroute = OptimizedRouteSerializer(read_only=True)
    locations = serializers.CharField(required=True)
    num_vehicles = serializers.IntegerField(required=True, min_value=1)

    class Meta:
        model = Optimizer
        fields = ['id', 'locations', 'depot', 'num_vehicles', 'matrix', 'optimizedroute']

    def create(self, validated_data):
        # no needed data to use for creating Optimized Route
        # validated_data.pop('optimizedroute')

        optimizer_instance = Optimizer.objects.create(**validated_data)
        OptimizedRoute.objects.create(optimizer=optimizer_instance)

        return optimizer_instance

    def update(self, instance, validated_data):
        # validated_data.pop('optimizedroute')

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        OptimizedRoute.objects.update_or_create(optimizer=instance)
        return instance

    def validate_locations(self, value):

        check, message = validate_locations_value(value)
        if not check:
            raise serializers.ValidationError(message)

        return value

    def validate_depot(self, value):

        check, message = validate_depot_value(self.initial_data.get('locations'), value)
        if not check:
            raise serializers.ValidationError(message)

        return value
