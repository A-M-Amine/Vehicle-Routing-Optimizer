from rest_framework import serializers
from .models import Optimizer
from api.optimized_route.models import OptimizedRoute
from api.vehicle.models import Vehicle
from .validators import validate_locations_value, validate_depot_value
from rest_framework.validators import UniqueValidator


class OptimizerSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True,
                                 validators=[UniqueValidator(queryset=Optimizer.objects.all())])
    locations = serializers.JSONField(required=True)
    vehicles = serializers.PrimaryKeyRelatedField(many=True, queryset=Vehicle.objects.all())
    solved = serializers.BooleanField(default=False)

    class Meta:
        model = Optimizer
        fields = '__all__'

    def create(self, validated_data):

        vehicles = validated_data.pop('vehicles')
        optimizer = Optimizer.objects.create(**validated_data)
        OptimizedRoute.objects.create(optimizer=optimizer)
        optimizer.vehicles.set(vehicles)
        return optimizer

    def update(self, instance, validated_data):
        vehicles = validated_data.pop('vehicles', None)

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        if vehicles is not None:
            instance.vehicles.set(vehicles)

        return instance

    def has_changed(self):
        # Get the instance data
        instance_data = self.to_representation(self.instance)
        # Get the validated data
        validated_data = self.validated_data
        # Compare the two data and return True if they are different
        for key in instance_data.keys() & validated_data.keys():
            if instance_data[key] != validated_data[key]:
                return True

        return False

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

    def validate_vehicles(self, value):

        if not value:
            raise serializers.ValidationError("At least one vehicle is required.")
        return value

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop('matrix')

        return data
