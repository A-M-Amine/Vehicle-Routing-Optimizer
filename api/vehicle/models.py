from django.db import models


# TODO validate vehicle data
class Vehicle(models.Model):
    name = models.CharField(max_length=150, null=True, blank=True)
    capacity = models.IntegerField(default=0)
    route_time = models.IntegerField(default=0)
