from rest_framework.permissions import BasePermission, SAFE_METHODS
from users.models import Subscription


def make_payment(request):
    # TODO
    pass


class IsStudentOrIsAdmin(BasePermission):
    message = 'Нет доступа к курсу'

    def has_permission(self, request, view):
        course_id = self._get_course_id(request)
        return self._is_admin(request) or self._is_student(request, course_id)

    def has_object_permission(self, request, view, obj):
        return self._is_admin(request) or self._is_student_with_permission(request, obj)

    def _get_course_id(self, request):
        return int(request.parser_context.get('kwargs').get('course_id'))

    def _is_admin(self, request):
        return request.user.is_staff

    def _is_student(self, request, course_id):
        return (
            request.user.is_authenticated and
            course_id in request.user.courses.values_list('id', flat=True)
        )

    def _is_student_with_permission(self, request, obj):
        return (
            request.user in obj.course.users and
            request.method in SAFE_METHODS
        )


class ReadOnlyOrIsAdmin(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_staff or request.method in SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or request.method in SAFE_METHODS
