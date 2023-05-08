from rest_framework import viewsets, status
from .serializers import OptimizedRouteSerializer
from .models import OptimizedRoute
from rest_framework.decorators import action
from rest_framework.response import Response
import json

from api.optimizer.models import Optimizer


class OptimizedRouteViewSet(viewsets.ModelViewSet):
    queryset = OptimizedRoute.objects.all()
    serializer_class = OptimizedRouteSerializer

    @action(detail=False, methods=['get'])
    def solutionById(self, request):

        pk = request.query_params.get('key')
        try:
            optimizer_instance = OptimizedRoute.objects.get(optimizer_id=pk)
        except Optimizer.DoesNotExist:
            return Response({'Error': f'Optimizer with id {pk} does not exist'}, status.HTTP_400_BAD_REQUEST)

        instance = OptimizedRouteSerializer(optimizer_instance)
        return Response(instance.data)
