from django.db import models
from api.optimizer.models import Optimizer


# TODO check for empty {} value of a vehicle path
class OptimizedRoute(models.Model):
    optimizer = models.ForeignKey(Optimizer, on_delete=models.CASCADE, blank=True, null=True)
    vehicle_routes = models.JSONField(default=dict)
