from django.db import models
from api.vehicle.models import Vehicle


# Create your models here.


class Optimizer(models.Model):
    name = models.CharField(max_length=150, unique=True, blank=True, null=True)
    locations = models.JSONField(default=dict)
    depot = models.IntegerField(default=0)
    vehicles = models.ManyToManyField(Vehicle)
    matrix = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.name}, depot index : {self.depot}"
