from rest_framework import serializers
from .models import Optimizer


class OptimizerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Optimizer
        fields = ['id', 'locations', 'depot', 'num_vehicles', 'matrix']
