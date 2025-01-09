from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from support_scheduler.ga import Scheduler

from .serializers import ScheduleRequestSerializer


@api_view(['POST'])
def get_schedule(request):
    serializer = ScheduleRequestSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        parameters = serializer.instance
        scheduler = Scheduler(parameters.schedule_parameters, parameters.genetic_algorithm_parameters)
        schedule = scheduler.generate_schedule()

        response = schedule

        return Response(response, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
