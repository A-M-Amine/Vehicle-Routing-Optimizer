from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Optimizer
from .serializers import OptimizerSerializer
from .solver import solver, route_matrix_via_api
from .validators import validate_locations_value
from api.optimized_route.models import OptimizedRoute, Vehicle
from api.optimized_route.serializers import OptimizedRouteSerializer
import json


class OptimizerViewSet(viewsets.ModelViewSet):
    # A view set for the Optimizer model
    queryset = Optimizer.objects.all()
    serializer_class = OptimizerSerializer

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def solver(self, request):
        self.get_object()
        pk = request.query_params.get('key')
        try:
            optimizer_instance = Optimizer.objects.get(id=pk)
        except Optimizer.DoesNotExist:
            return Response({'Error': f'Optimizer with id {pk} does not exist'})

        optimizer_serializer = OptimizerSerializer(optimizer_instance)
        matrix = optimizer_serializer.data['matrix']
        depot = optimizer_serializer.data['depot']
        num_vehicles = optimizer_serializer.data['num_vehicles']
        locations = json.loads(optimizer_serializer.data['locations'])

        result = solver(locations=locations, matrix=matrix, depot=depot, num_vehicles=num_vehicles)

        # TODO:  add name here
        # get the optimized route linked to the optimizer and update it with the data
        opt_route_instance = OptimizedRoute.objects.get(optimizer=optimizer_instance)
        optimized_route_serializer = OptimizedRouteSerializer(data=result)
        if optimized_route_serializer.is_valid():
            optimized_route_serializer.update(instance=opt_route_instance, validated_data=result)
        else:
            return Response({"error": "check data"})

        return Response(result)

    @action(detail=False, methods=['get', 'post'], url_path="create-matrix", url_name="create-matrix")
    def create_matrix(self, request):

        pk = request.query_params.get('key')
        try:
            optimizer_instance = Optimizer.objects.get(id=pk)
        except Optimizer.DoesNotExist:
            return Response({'Error': f'Optimizer with id {pk} does not exist'})

        optimizer = OptimizerSerializer(optimizer_instance)
        if optimizer.data['matrix'] != {}:
            return Response({'error': 'Distance & Time matrix already exist'})

        matrix = route_matrix_via_api(json.loads(optimizer.data['locations']))
        optimizer_instance = optimizer.update(instance=optimizer_instance, validated_data=matrix)
        optimizer = OptimizerSerializer(optimizer_instance)

        return Response(optimizer.data)
