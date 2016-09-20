from django.contrib.auth.models import User, Group
from rest_framework import serializers
from . models import Test, Task, Subject, PossibleAnswer, UserAnswer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'groups')


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name')


class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject


class PossibleAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = PossibleAnswer
        fields = ('id', 'text', 'is_true')


class UserAnswerSerializer(serializers.ModelSerializer):
    answers = PossibleAnswerSerializer(many=True, read_only=True)

    class Meta:
        model = UserAnswer
        fields = ('id', 'user', 'test', 'task', 'answers', 'time_of_answer')


class TaskSerializer(serializers.ModelSerializer):
    possible_answers = PossibleAnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = ('id', 'number', 'question', 'question_type',
                  'possible_answers')
