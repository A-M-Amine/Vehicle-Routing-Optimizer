import numbers
from rest_framework import serializers
from .models import Optimizer, Delivery, default_time_window_dict
from api.optimized_route.models import OptimizedRoute
from api.vehicle.models import Vehicle
from .validators import validate_coords
from rest_framework.validators import UniqueValidator


class DeliverySerializer(serializers.ModelSerializer):
    coordinates = serializers.JSONField(required=True)
    package_size = serializers.IntegerField()
    time_window = serializers.JSONField(default=default_time_window_dict)

    class Meta:
        model = Delivery
        fields = '__all__'

    def validate_coordinates(self, value):

        check, msg = validate_coords(value)
        if not check:
            raise serializers.ValidationError(msg)

        return value

    def validate_time_window(self, value):

        if not isinstance(value, list) or len(value) != 2:
            raise serializers.ValidationError('(value)s is not a valid time window')

        # Check that the items are valid time values
        for item in value:
            if not isinstance(item, numbers.Real):
                raise serializers.ValidationError(f'{item} is not a valid type for time')
            if item < 0:
                raise serializers.ValidationError(f'{item} is not a valid time')

        if value[0] > value[1]:
            raise serializers.ValidationError(f'{value[0]} > {value[1]}, [time1, time2] time1 should be earlier than '
                                              f'time2')

        return value


class OptimizerSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True,
                                 validators=[UniqueValidator(queryset=Optimizer.objects.all())])
    depot = serializers.JSONField(required=True)
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

    def validate_depot(self, value):

        check, msg = validate_coords(value)
        if not check:
            raise serializers.ValidationError(msg)

        return value

    def validate_vehicles(self, value):

        if not value:
            raise serializers.ValidationError("At least one vehicle is required.")
        return value

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return data
