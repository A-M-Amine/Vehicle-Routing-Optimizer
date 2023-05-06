from django.db import models


class Vehicle(models.Model):
    name = models.CharField(max_length=150, null=True, blank=True)
    capacity = models.IntegerField(default=0)
