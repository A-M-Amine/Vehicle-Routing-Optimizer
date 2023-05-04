from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Optimizer
from .serializers import OptimizerSerializer
from .solver import solver, route_matrix_via_api, tester
from .validators import validate_locations_value
from api.optimized_route.models import OptimizedRoute
from api.optimized_route.serializers import OptimizedRouteSerializer
import json


class OptimizerViewSet(viewsets.ModelViewSet):
    # A view set for the Optimizer model
    queryset = Optimizer.objects.all()
    serializer_class = OptimizerSerializer

    def perform_update(self, serializer):
        # Check if the serializer data has changed
        if serializer.has_changed():
            # Set the solved field to False
            serializer.instance.solved = False
        # Save the serializer data
        serializer.save()

    @action(detail=True, methods=['get'])
    def solver(self, request, pk=None):

        optimizer_instance = self.get_object()

        optimizer_serializer = OptimizerSerializer(optimizer_instance)

        solved = optimizer_serializer.data['solved']
        if solved:
            return Response({"Success": "solution already exists"})

        depot = optimizer_serializer.data['depot']
        vehicles = optimizer_serializer.data['vehicles']
        locations = optimizer_serializer.data['locations']
        matrix = optimizer_serializer.data['matrix']

        if matrix['locations'] != locations:
            matrix = route_matrix_via_api(locations)
            optimizer_instance = optimizer_serializer.update(instance=optimizer_instance,
                                                             validated_data=matrix)
            optimizer_instance.save()
            matrix = matrix['matrix']

        check, result = solver(locations, matrix, vehicles, depot)
        if not check:
            return Response(result)

        # get the optimized route linked to the optimizer and update it with the data
        try:
            solved = {'solved': True}
            optimizer_serializer.update(instance=optimizer_instance, validated_data=solved)
            optimizer_instance.save()
            opt_route_instance = OptimizedRoute.objects.get(optimizer=optimizer_instance)
            optimized_route_serializer = OptimizedRouteSerializer(data=result)
            if optimized_route_serializer.is_valid():
                optimized_route_serializer.update(instance=opt_route_instance, validated_data=result)
            else:
                return Response({"error": "check data"})

        except OptimizedRoute.DoesNotExist:
            return Response({"error": "optimized route linked to this optimizer should be created first"})

        return Response({"Success": "Solution Found"})
