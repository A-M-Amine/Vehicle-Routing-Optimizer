from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Optimizer, Delivery
from .serializers import OptimizerSerializer, DeliverySerializer
from .solver import solver, route_matrix_via_api
from api.optimized_route.models import OptimizedRoute
from api.optimized_route.serializers import OptimizedRouteSerializer


# TODO add update in bulk
class DeliveryViewSet(viewsets.ModelViewSet):
    queryset = Delivery.objects.all()
    serializer_class = DeliverySerializer

    def create(self, request, *args, **kwargs):
        # Deserialize the incoming data into a list of dictionaries
        data = request.data
        if not isinstance(data, list):
            return Response({'error': 'Expected a list of items'}, status=status.HTTP_400_BAD_REQUEST)

        # Iterate through the list of dictionaries and create a Delivery object for each dictionary
        created_deliveries = []
        for delivery_data in data:
            serializer = self.get_serializer(data=delivery_data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            created_deliveries.append(serializer.instance)

        # Serialize the created objects and return them in the response
        response_serializer = self.get_serializer(created_deliveries, many=True)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, optimizer_pk, *args, **kwargs):
        # Deserialize the incoming data into a list of dictionaries
        data = request.data
        if not isinstance(data, list):
            return Response({'error': 'Expected a list of items'}, status=status.HTTP_400_BAD_REQUEST)
        # Get the optimizer object from the optimizer_pk parameter
        optimizer = get_object_or_404(Optimizer, pk=optimizer_pk)
        # Iterate through the list of dictionaries and update a Delivery object for each dictionary
        updated_deliveries = []
        for delivery_data in data:
            # Get the Delivery object by its id and optimizer or raise an exception if not found
            delivery = get_object_or_404(Delivery, id=delivery_data.get('id'), optimizer=optimizer)
            # Use the partial argument to allow partial updates
            serializer = self.get_serializer(delivery, data=delivery_data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            updated_deliveries.append(serializer.instance)
        # Serialize the updated objects and return them in the response
        response_serializer = self.get_serializer(updated_deliveries, many=True)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def list(self, request, optimizer_pk):
        # get the optimizer object from the optimizer_pk parameter
        optimizer = get_object_or_404(Optimizer, pk=optimizer_pk)
        # get the deliveries that belong to the optimizer
        deliveries = Delivery.objects.filter(optimizer=optimizer)
        # serialize the deliveries
        serializer = DeliverySerializer(deliveries, many=True)
        # return a response with the serialized data
        return Response(serializer.data)

    def retrieve(self, request, optimizer_pk, pk):
        # get the optimizer object from the optimizer_pk parameter
        optimizer = get_object_or_404(Optimizer, pk=optimizer_pk)
        # get the delivery object from the pk parameter
        delivery = get_object_or_404(Delivery, pk=pk)
        # check if the delivery belongs to the optimizer
        if delivery.optimizer != optimizer:
            # return a 404 response if not
            return Response(status=status.HTTP_404_NOT_FOUND)
        # serialize the delivery
        serializer = DeliverySerializer(delivery)
        # return a response with the serialized data
        return Response(serializer.data)


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

        solving_method = request.query_params.get('solving_method')

        optimized_route = OptimizedRoute.objects.get(optimizer=optimizer_instance)

        solved = optimizer_serializer.data['solved']
        if optimized_route.local_search_algorithm == solving_method and solved:
            return Response({"Success": "solution already exists"})

        check, result = solver(optimizer_instance, solving_method)
        if not check:
            msg = result
            result = {
                "vehicle_routes": []
            }

        # get the optimized route linked to the optimizer and update it with the data
        try:
            opt_route_instance = OptimizedRoute.objects.get(optimizer=optimizer_instance)
            optimized_route_serializer = OptimizedRouteSerializer(data=result)
            if optimized_route_serializer.is_valid():
                optimized_route_serializer.update(instance=opt_route_instance, validated_data=result)
            else:
                return Response({"error": "check data"}, status=status.HTTP_400_BAD_REQUEST)

        except OptimizedRoute.DoesNotExist:
            return Response({"error": "optimized route linked to this optimizer should be created first"},
                            status=status.HTTP_400_BAD_REQUEST)

        if not check:
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)

        solved = {'solved': True}
        optimizer_serializer.update(instance=optimizer_instance, validated_data=solved)
        optimizer_instance.save()

        return Response({"Success": "Solution Found"})
