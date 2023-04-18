from django.db import models
from api.optimizer.models import Optimizer
# Create your models here.


class OptimizedRoute(models.Model):
    name = models.CharField(max_length=150, blank=True, null=True)
    optimizer = models.ForeignKey(Optimizer, on_delete=models.CASCADE, blank=True, null=True)


class Vehicle(models.Model):

    route = models.ForeignKey(OptimizedRoute, on_delete=models.CASCADE, blank=True, null=True)
    vehicle_id = models.IntegerField(default=0)
    path = models.JSONField(default=dict)
    route_time = models.IntegerField(default=0)


