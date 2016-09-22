from rest_framework import permissions


class UserPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method == 'GET':
            return request.user.is_authenticated()
        else:
            return request.user.is_authenticated() and request.user.is_staff
