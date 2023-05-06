from django.contrib import admin
from .models import Optimizer, Delivery

# Register your models here.


admin.site.register(Optimizer)
admin.site.register(Delivery)

# add get_queryset to improve perfomance while displaying the list of routes
