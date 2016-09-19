from django.db import models
from django.contrib.auth.models import User


class Subject(models.Model):
    """ The subject of the test. """
    title = models.CharField(max_length=255)

    def __str__(self):
        return '<Subject: %s>' % self.title


class Task(models.Model):
    """ The one of the tasks to the test. """

    # The question can be text, or url to audio or video
    question = models.TextField(help_text='text of the question')
    number = models.PositiveSmallIntegerField(help_text='serial number of task')

    QUESTION_TYPES = (
        ('aud', 'Audio'),
        ('vid', 'Video'),
        ('txt', 'Text')
    )
    question_type = models.CharField(max_length=3, choices=QUESTION_TYPES)

    def __str__(self):
        return '<Task #%d>' % self.number


class PossibleAnswer(models.Model):
    """
    The one of the possible answers to the task. Every task can have
    a few possible answers, but each answer can have only one task.
    The possible answer can be true or false.
    """
    text = models.TextField(help_text='text of the answer')
    task = models.ForeignKey(Task, related_name='possible_answers')
    is_true = models.BooleanField(default=False, help_text='correct answer')


class Test(models.Model):
    """ The test with list of tasks. """
    title = models.CharField(max_length=255)
    subject = models.ForeignKey(Subject, related_name='test',
                                blank=True, null=True)
    tasks = models.ManyToManyField(Task, related_name='tests')


class UserAnswer(models.Model):
    """ The answer of user. """
    user = models.ForeignKey(User, related_name='user_answers')
    task = models.ForeignKey(Task, related_name='user_answers')
    test = models.ManyToManyField(Test, related_name='user_answers')
    answers = models.ManyToManyField(PossibleAnswer,
                                     related_name='user_answers')
    time_of_answer = models.DateTimeField(auto_now=True)
