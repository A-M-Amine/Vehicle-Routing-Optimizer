from django.urls import path, include
from .views import home
from rest_framework.authtoken import views

urlpatterns = [
    path('', home, name='api.home'),
    path('', include('api.optimizer.urls')),
    path('optimizedroute/', include('api.optimized_route.urls')),
    path('vehicle/', include('api.vehicle.urls')),
]
