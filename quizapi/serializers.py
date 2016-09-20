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
        fields = ('id', 'user', 'test', 'task', 'answers', 'time_of_answer')


class TaskSerializer(serializers.ModelSerializer):
    possible_answers = PossibleAnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = ('id', 'number', 'question', 'question_type',
                  'possible_answers')


class TestSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)
    subject = SubjectSerializer()

    class Meta:
        model = Test
        fields = ('id', 'title', 'subject', 'tasks')
