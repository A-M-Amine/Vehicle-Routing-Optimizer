from django.db import models


# Create your models here.


class Optimizer(models.Model):
    locations = models.JSONField(default=dict)
    depot = models.IntegerField(default=0)
    num_vehicles = models.IntegerField(default=1)
    matrix = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return str(self.id)
