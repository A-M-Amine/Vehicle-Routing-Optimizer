from django.contrib import admin
from .models import Optimizer
# Register your models here.


admin.site.register(Optimizer)


# add get_queryset to improve perfomance while displaying the list of routes
