from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Optimizer, Delivery
from .serializers import OptimizerSerializer, DeliverySerializer
from .solver import solver, route_matrix_via_api, tester
from api.optimized_route.models import OptimizedRoute
from api.optimized_route.serializers import OptimizedRouteSerializer


# TODO fix HTTP ERROR Responses Type

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

        check, result = solver(optimizer_instance)
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
