from quizapi.models import Test, TestSession, UserAnswer


def is_started_test_session(user_id, test_id):
    """
    Returns true if the test session for the given test and user is started.
    """
    test = Test.objects.get(pk=test_id)

    active_test_session = test.test_session.filter(
        user_id=user_id,
        finish_datetime=None
    )
    return active_test_session.count() == 1


def get_current_test_session(user_id, test_id):
    """
    Returns started session for these test and user or returns
    None if it doesn't exists.
    """
    test = Test.objects.get(pk=test_id)

    active_test_session = test.test_session.filter(
        user_id=user_id,
        finish_datetime=None
    )
    if active_test_session.count() == 1:
        return active_test_session.first()
    else:
        return None


def is_answered_task(test_session_id, task_id):
    """
    Returns true if the given task is already answered in the test session.
    """
    test_session = TestSession.objects.get(pk=test_session_id)
    try:
        return test_session.user_answers.filter(task_id=task_id).count() > 0
    except UserAnswer.DoesNotExist:
        return False


def count_answered_tasks(user_id, test_session_id):
    test_session = TestSession.objects.get(pk=test_session_id)
    return UserAnswer.objects.filter(test_session_id=test_session.pk,
                                     user_id=user_id).count()


def count_tasks(test_id):
    test = Test.objects.get(pk=test_id)
    return test.tasks.all().count()


def is_test_completed(user_id, test_session_id):
    test_id = TestSession.objects.get(pk=test_session_id).test_id
    print(count_answered_tasks(user_id, test_session_id), count_tasks(test_id))
    return count_tasks(test_id) == count_answered_tasks(user_id, test_session_id)
