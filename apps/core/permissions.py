from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin_role


class IsTeacherRole(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_teacher_role


class IsStudentRole(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_student_role


class IsParentRole(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == request.user.Roles.PARENT


class IsAdminOrTeacher(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_admin_role or request.user.is_teacher_role
        )


class IsOwnerOrAdmin(BasePermission):
    """Object-level: user owns the object or is admin."""

    def has_object_permission(self, request, view, obj):
        if request.user.is_admin_role:
            return True
        return getattr(obj, "student_id", None) == request.user.pk or getattr(obj, "recipient_id", None) == request.user.pk


class IsAdminOrTeacherRole(IsAdminOrTeacher):
    pass


class ReadOnlyOrAdminRole(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_admin_role


class IsApprovedUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.registration_status == "approved" or request.user.is_superuser
        )
