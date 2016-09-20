from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework.decorators import api_view, detail_route
from rest_framework.response import Response
from rest_framework.views import APIView

from quizapi.serializers import UserAnswerSerializer
from .models import Test, Subject, PossibleAnswer, UserAnswer, Task
from . import serializers


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = serializers.UserSerializer

    @detail_route(methods=['get'])
    def get_tests(self, request, pk=None):
        """
        Returns the list with stats about tests which are
        started or finished by user.
        """
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'detail': 'Not found'})
        answers = [UserAnswerSerializer(a) for a in user.user_answers.all()]

        return Response({'tests': answers})


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = serializers.GroupSerializer


class TestViewSet(viewsets.ModelViewSet):
    queryset = Test.objects.all()
    serializer_class = serializers.TestSerializer


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = serializers.SubjectSerializer


class PossibleAnswerViewSet(viewsets.ModelViewSet):
    queryset = PossibleAnswer.objects.all()
    serializer_class = serializers.PossibleAnswerSerializer


class UserAnswerViewSet(viewsets.ModelViewSet):
    queryset = UserAnswer.objects.all()
    serializer_class = serializers.UserAnswerSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = serializers.TaskSerializer

