import datetime

from django.contrib.auth.models import User, Group
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import detail_route, api_view
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest_framework.response import Response
from social.apps.django_app.utils import load_strategy, load_backend
from social.backends.oauth import BaseOAuth1, BaseOAuth2
from social.exceptions import AuthAlreadyAssociated

from .permissions import UserPermission, IsAuthenticatedOrCreate
from .utils import responses,queries
from .models import Test, Subject, PossibleAnswer, UserAnswer, Task, TestSession
from . import serializers


class SocialSignUpView(viewsets.generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.SocialSignUpSerializer
    permission_classes = (IsAuthenticatedOrCreate, )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        provider = request.data['provider']
        authed_user = request.user if not request.user.is_anonymous() else None
        strategy = load_strategy(request)
        backend = load_backend(
            strategy=strategy,
            name=provider,
            redirect_uri=None
        )
        if isinstance(backend, BaseOAuth1):
            token = {
                'oauth_token': request.data['access_token'],
                'oauth_token_secret': request.data['access_token_secret']
            }
        elif isinstance(backend, BaseOAuth2):
            token = request.data['access_token']

        try:
            user = backend.do_auth(token, user=authed_user)
        except AuthAlreadyAssociated:
            return responses.response_400(
                'That social media account is already in use')

        if user and user.is_active:
            auth_created = user.social_auth.get(provider=provider)
            if not auth_created.extra_data['access_token']:
                auth_created.extra_data['access_token'] = token
                auth_created.save()

            serializer.instance = user
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED,
                            headers=headers)

        else:
            return responses.response_400('Error with social authentication')


class UserPermissionsViewSet(viewsets.ModelViewSet):
    """
    The ModelViewSet which allows GET method authenticated
    users and allows other methods only for admins.
    """
    permission_classes = (UserPermission,)


class TestViewSet(UserPermissionsViewSet):
    queryset = Test.objects.all()
    serializer_class = serializers.TestSerializer

    def list(self, request, *args, **kwargs):
        queryset = Test.objects.all()
        if not queryset:
            return responses.response_404()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if queries.is_started_test_session(request.user.id, instance.pk):
            serializer = serializers.TestDetailSerializer(instance)
        else:
            serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @detail_route(methods=['POST'], permission_classes=(IsAuthenticated,))
    def start_test(self, request, pk=None):
        """ Starts test session for the given test. """
        try:
            if queries.is_started_test_session(request.user.id, pk):
                return responses.response_400(
                    'Test session is already started')
        except Test.DoesNotExist:
            return responses.response_404()

        test_session = TestSession(test_id=pk, user_id=request.user.id)
        test_session.save()

        return Response(serializers.TestSessionSerializer(test_session).data)


class NestedTestSessionStatsViewSet(UserPermissionsViewSet):
    """ Stats for tests sessions. """
    queryset = TestSession.objects.all()
    serializer_class = serializers.TestSessionStatsSerializer

    def list(self, request, **kwargs):
        queryset = TestSession.objects.filter(user_id=request.user.id,
                                              test_id=kwargs['test_pk'])
        if queryset.count() == 0:
            return responses.response_404(
                'Not found stats for user #%s and test #%s'
                % (request.user.id, kwargs['test_pk'])
            )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)


class NestedTaskViewSet(UserPermissionsViewSet):
    """ Tasks for tests. """
    serializer_class = serializers.TaskDetailSerializer
    queryset = Task.objects.all()

    def list(self, request, **kwargs):
        test = Test.objects.filter(pk=kwargs['test_pk'])
        if test.count() == 0:
            return responses.response_404('Not found test with id '
                                          + kwargs['test_pk'])

        if not queries.is_started_test_session(request.user.id,
                                               test.first().pk):
                if not request.user.is_staff:
                    return responses.response_400(
                        'Permission denied. There are not started sessions.')

        queryset = test.first().tasks.all()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not queries.is_started_test_session(request.user.id,
                                               kwargs['test_pk']):
            if not request.user.is_staff:
                return responses.response_400(
                    'Permission denied. There are not started sessions.')

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

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

    @detail_route(methods=['POST'], permission_classes=(IsAuthenticated,))
    def answer(self, request, test_pk=None, pk=None):
        """
        Answers to the given task for the given test. It closes test session
        after the answer to the last task.
        """
        try:
            test = Test.objects.get(pk=test_pk)
            answers = test.tasks.get(pk=pk).possible_answers.all()
        except (Test.DoesNotExist, Task.DoesNotExist):
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

        if queries.is_test_completed(request.user.id, test_session.pk):
            test_session.finish_datetime = datetime.datetime.now()
            test_session.save()

        return Response(serializers.UserAnswerSerializer(user_answer).data)


@api_view()
def about_me(requests):
    user = User.objects.get(pk=requests.user.id)
    return Response(serializers.UserSerializer(user).data)


class AdminPermissionsViewSet(viewsets.ModelViewSet):
    """ The ModelViewSet which allowed only for admins. """
    permission_classes = (IsAdminUser,)


class UserViewSet(AdminPermissionsViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = serializers.UserSerializer

    def get_permissions(self):
        return (AllowAny() if self.request.method == 'POST'
                else IsAdminUser()),


class GroupViewSet(AdminPermissionsViewSet):
    queryset = Group.objects.all()
    serializer_class = serializers.GroupSerializer


class SubjectViewSet(AdminPermissionsViewSet):
    queryset = Subject.objects.all()
    serializer_class = serializers.SubjectSerializer


class PossibleAnswerViewSet(AdminPermissionsViewSet):
    queryset = PossibleAnswer.objects.all()
    serializer_class = serializers.PossibleAnswerSerializer


class UserAnswerViewSet(AdminPermissionsViewSet):
    queryset = UserAnswer.objects.all()
    serializer_class = serializers.UserAnswerSerializer


class TaskViewSet(AdminPermissionsViewSet):
    queryset = Task.objects.all()
    serializer_class = serializers.TaskDetailSerializer
