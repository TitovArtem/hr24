from django.conf.urls import url, include
from rest_framework import routers
from rest_framework.authtoken import views as auth_views
from rest_framework_nested.routers import NestedSimpleRouter

from quizapi import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'tests', views.TestViewSet)
router.register(r'subjects', views.SubjectViewSet)
router.register(r'tasks', views.TaskViewSet)
router.register(r'answers', views.PossibleAnswerViewSet)
router.register(r'stats', views.PossibleAnswerViewSet)

tests_router = NestedSimpleRouter(router, r'tests', lookup='test')
tests_router.register(r'tasks', views.NestedTaskViewSet)
tests_router.register(r'stats', views.NestedTestSessionStatsViewSet)

app_name = 'api'

urlpatterns = [
    url(r'^', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^', include(router.urls)),
    url(r'^', include(tests_router.urls)),
    url(r'^get_token/', auth_views.obtain_auth_token),
    url(r'^about_me/$', views.about_me)
]
