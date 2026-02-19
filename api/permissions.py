from rest_framework import permissions

class IsDirector(permissions.BasePermission):
    """Permission pour les directeurs uniquement"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'directeur'

class IsCoordinator(permissions.BasePermission):
    """Permission pour les coordinateurs"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'coordinateur'

class IsDepartmentHead(permissions.BasePermission):
    """Permission pour les chefs de département"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['coordinateur', 'directeur']
    
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'department'):
            return request.user.department == obj.department
        return True

class IsSectionHead(permissions.BasePermission):
    """Permission pour les responsables de section"""
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'section'):
            return request.user.section == obj.section
        return request.user.role in ['directeur', 'coordinateur', 'responsable_section']

class CanManageTeam(permissions.BasePermission):
    """Permission pour ceux qui peuvent gérer une équipe"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.can_manage_team()

class CanCreateProject(permissions.BasePermission):
    """Permission pour ceux qui peuvent créer des projets"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.can_create_projects()

class CanValidateTask(permissions.BasePermission):
    """Permission pour ceux qui peuvent valider des tâches"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.can_validate_tasks()