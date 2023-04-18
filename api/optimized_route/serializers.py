from rest_framework import serializers
from .models import OptimizedRoute, Vehicle


class VehicleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Vehicle
        fields = '__all__'


class OptimizedRouteSerializer(serializers.ModelSerializer):
    vehicle_routes = VehicleSerializer(many=True, read_only=True)

    class Meta:

        model = OptimizedRoute
        fields = '__all__'

    def create(self, validated_data):
        vehicle_data = validated_data.pop('vehicle_routes')
        optimized_route_instance = OptimizedRoute.objects.create(**validated_data)
        for vehicle in vehicle_data:
            Vehicle.objects.create(route=optimized_route_instance, **vehicle)
        return optimized_route_instance

    def update(self, instance, validated_data):
        vehicle_data = validated_data.pop('vehicle_routes')
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        for vehicle in vehicle_data:
            Vehicle.objects.update_or_create(route=instance, vehicle_id=vehicle['vehicle_id'],
                                             path=vehicle['path'], route_time=vehicle['route_time'])
        return instance

    def to_representation(self, instance):

        data = super().to_representation(instance)
        request = self.context['request']
        vehicles = Vehicle.objects.all().filter(route=instance)
        serialized_vehicles = VehicleSerializer(vehicles, many=True)
        data['vehicle_routes'] = serialized_vehicles.data
        return data
