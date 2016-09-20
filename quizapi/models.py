from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """
    This function is triggered whenever a new user has been
    added to database.
    """
    if created:
        Token.objects.create(user=instance)


class Subject(models.Model):
    """ The subject of the test. """
    title = models.CharField(max_length=255, unique=True)

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

    def __str__(self):
        return '<PossibleAnswer: id %d>' % self.pk


class Test(models.Model):
    """ The test with list of tasks. """
    title = models.CharField(max_length=255)
    subject = models.ForeignKey(Subject, related_name='test',
                                blank=True, null=True)
    tasks = models.ManyToManyField(Task, related_name='tests')

    def __str__(self):
        return '<Test: %s>' % self.title


class TestSession(models.Model):
    """
    The session of test. It contains the start and finish
    date times for each test of each user
    """
    test = models.ForeignKey(Test, related_name='test_session')
    user = models.ForeignKey(User, related_name='test_session')
    start_datetime = models.DateTimeField(auto_now_add=True,
                                          help_text='session start datetime')
    finish_datetime = models.DateTimeField(auto_now_add=True,
                                           blank=True,
                                           null=True,
                                           help_text='session finish datetime')

    def __str__(self):
        return '<TestSession: [Test #%d] from %s to %s by %s>' % \
               (self.test.title, self.start_datetime,
                self.finish_datetime, self.user.name)


class UserAnswer(models.Model):
    """ The answer of user. """
    user = models.ForeignKey(User, related_name='user_answers')
    task = models.ForeignKey(Task, related_name='user_answers')
    test = models.ManyToManyField(Test, related_name='user_answers')
    answers = models.ManyToManyField(PossibleAnswer,
                                     related_name='user_answers')
    answered_datetime = models.DateTimeField(
        auto_now=True, help_text='datetime when user answered')
