import datetime

from django.contrib.auth.models import User, Group
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response


from .utils import responses,queries
from .serializers import UserAnswerSerializer, TaskSerializer
from .models import Test, Subject, PossibleAnswer, UserAnswer, Task, TestSession
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


class TestViewSet(viewsets.ModelViewSet):
    queryset = Test.objects.all()
    serializer_class = serializers.TestSerializer

    @detail_route(methods=['POST'])
    def start_test(self, request, pk=None):
        try:
            if queries.is_started_test_session(request.user.id, pk):
                return responses.response_400(
                    'Test session is already started')
        except Test.DoesNotExist:
            return responses.response_404()

        test_session = TestSession(test_id=pk, user_id=request.user.id)
        test_session.save()

        return Response(serializers.TestSessionSerializer(test_session).data)

    @detail_route(methods=['GET'])
    def stats(self, request, pk=None):
        try:
            test = Test.objects.get(pk=pk)
        except Test.DoesNotExist as e:
            return responses.response_404()

        test_sessions = test.test_session.filter(user_id=request.user.id)
        if not test_sessions:
            return responses.response_400('There are not sessions of this test')

        page = self.paginate_queryset(test_sessions)
        if page is not None:
            serializer = serializers.TestSessionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = serializers.TestSessionSerializer(test_sessions, many=True)

        return Response(serializer.data)


class NestedTaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = serializers.TaskSerializer

    def _get_answers(self, params, answers):
        vars, vars_set = [], set()
        for key, val in params.items():
            val = int(val)
            if val in vars_set:
                continue
            else:
                vars_set.add(val)

            answer = answers.get(id=val)
            vars.append(answer)
        return vars

    @detail_route(methods=['POST'])
    def answer(self, request, test_pk=None, pk=None):
        try:
            test = Test.objects.get(pk=test_pk)
            answers = test.tasks.get(pk=pk).possible_answers.all()
        except Test.DoesNotExists:
            return responses.response_404()

        test_session = queries.get_current_test_session(
            request.user.id, test_pk)
        if not test_session:
            return responses.response_400('There are not started sessions')

        if queries.is_answered_task(test_session.pk, pk):
            return responses.response_400('This task is already answered')

        if not answers:
            return responses.response_400('There are not possible answers')

        if answers.count() < len(request.query_params):
            return responses.response_400('Too many answers')

        try:
            vars = self._get_answers(request.query_params, answers)
        except ValueError:
            return responses.response_400('Not int parameter')
        except PossibleAnswer.DoesNotExist:
            return responses.response_400('Invalid answer index')

        user_answer = UserAnswer(
            user_id=request.user.id,
            test_session_id=test_session.pk,
            task_id=pk
        )
        user_answer.save()

        for v in vars:
            user_answer.answers.add(v)

        print(test_session.pk)
        if queries.is_test_completed(request.user.id, test_session.pk):
            test_session.finish_datetime = datetime.datetime.now()
            test_session.save()

        return Response(serializers.UserAnswerSerializer(user_answer).data)


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = serializers.GroupSerializer


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
