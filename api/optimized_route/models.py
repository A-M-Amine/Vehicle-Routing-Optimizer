from django.db import models
from api.optimizer.models import Optimizer


# TODO check for empty {} value of a vehicle path
class OptimizedRoute(models.Model):
    optimizer = models.ForeignKey(Optimizer, on_delete=models.CASCADE, blank=True, null=True)
    local_search_algorithm = models.CharField(max_length=50, default='')
    vehicle_routes = models.JSONField(default=dict)
    total_time = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)
    total_distance = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)
