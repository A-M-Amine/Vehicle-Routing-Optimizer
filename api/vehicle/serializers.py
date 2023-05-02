from rest_framework import serializers
from .models import Vehicle
import json


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = '__all__'

