import base64

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User, Group
from rest_framework import serializers

from .utils import queries
from . models import Test, Task, Subject, PossibleAnswer, UserAnswer, \
    TestSession


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name',
                  'groups', 'password')
        write_only_fields = ('password',)
        read_only_fields = ('id',)

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
        )

        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.set_password(password)

        return super(UserSerializer, self).update(instance, validated_data)


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name')


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject


class PossibleAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = PossibleAnswer
        fields = ('id', 'text')


class UserAnswerSerializer(serializers.ModelSerializer):
    answers = PossibleAnswerSerializer(many=True, read_only=True)

    class Meta:
        model = UserAnswer
        fields = ('id', 'user', 'test_session', 'task',
                  'answers', 'answered_datetime')


class TaskDetailSerializer(serializers.ModelSerializer):
    possible_answers = PossibleAnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = ('id', 'number', 'question', 'question_type',
                  'possible_answers')


class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = ('id', 'number', 'question', 'question_type')


class TestDetailSerializer(serializers.ModelSerializer):
    tasks = TaskDetailSerializer(many=True, read_only=True)
    subject = SubjectSerializer()

    class Meta:
        model = Test
        fields = ('id', 'title', 'subject', 'tasks')


class TestSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer()

    class Meta:
        model = Test
        fields = ('id', 'title', 'subject')


class TestSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestSession
        fields = ('id', 'test', 'user', 'start_datetime', 'finish_datetime')


class TestSessionStatsSerializer(serializers.ModelSerializer):
    test_stats = serializers.SerializerMethodField('get_stats')

    class Meta:
        model = TestSession
        fields = ('id', 'test', 'user', 'start_datetime',
                  'finish_datetime', 'test_stats')

    def get_stats(self, obj):
        return {'tasks_count': queries.count_tasks(obj.test_id),
                'correct_answers': queries.count_correct_answers(obj.pk)}


class SocialSignUpSerializer(UserSerializer):
    client_id = serializers.SerializerMethodField()
    client_secret = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('client_id', 'client_secret')

    def get_client_id(self, obj):
        return obj.application_set.first().client_id

    def get_client_secret(self, obj):
        return obj.application_set.first().client_secret
