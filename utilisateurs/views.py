from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from .models import User, Poste, Department, Section, Competence, UserActivity
from .serializers import (
    UserListSerializer, UserDetailSerializer, UserCreateUpdateSerializer,
    PosteSerializer, DepartmentSerializer, SectionSerializer,
    CompetenceSerializer, UserActivitySerializer
)
from api.permissions import IsDirector, IsCoordinator, IsDepartmentHead
from core.pagination import StandardResultsSetPagination
from core.mixins import ActivityLoggerMixin

class UserViewSet(viewsets.ModelViewSet, ActivityLoggerMixin):
    queryset = User.objects.all().select_related('department', 'section', 'poste')
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'is_active', 'department', 'section', 'poste']
    search_fields = ['email', 'first_name', 'last_name', 'phone']
    ordering_fields = ['last_name', 'first_name', 'date_joined', 'last_login']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return UserListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return UserCreateUpdateSerializer
        return UserDetailSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsDirector|IsCoordinator|IsDepartmentHead]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsDirector|IsCoordinator]
        else:
            permission_classes = [IsDirector]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Filtrer selon le rôle
        if user.role == 'coordinateur':
            return queryset
        elif user.role == 'responsable_section' and user.section:
            return queryset.filter(section=user.section)
        elif user.role == 'membre':
            return queryset.filter(id=user.id)
        return queryset
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Statistiques des utilisateurs"""
        data = {
            'total': User.objects.count(),
            'active': User.objects.filter(is_active=True).count(),
            'by_role': User.objects.values('role').annotate(count=Count('id')),
            'by_department': User.objects.values(
                'department__name', 'department__color'
            ).annotate(count=Count('id')).order_by('-count'),
            'recent_joined': UserListSerializer(
                User.objects.order_by('-date_joined')[:10], many=True
            ).data,
        }
        return Response({'status': 'success', 'data': data})
    
    @action(detail=True, methods=['get'])
    def team(self, request, pk=None):
        """Récupérer l'équipe d'un utilisateur"""
        user = self.get_object()
        team = user.get_team_members()
        serializer = UserListSerializer(team, many=True)
        return Response({'status': 'success', 'data': serializer.data})
    
    @action(detail=False, methods=['get'])
    def me_team(self, request):
        """Récupérer mon équipe"""
        team = request.user.get_team_members()
        serializer = UserListSerializer(team, many=True)
        return Response({'status': 'success', 'data': serializer.data})

class PosteViewSet(viewsets.ModelViewSet):
    queryset = Poste.objects.all()
    serializer_class = PosteSerializer
    permission_classes = [IsDirector|IsCoordinator]
    filter_backends = [filters.SearchFilter]
    search_fields = ['titre', 'code']

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all().annotate(
        user_count=Count('utilisateurs', distinct=True),
        project_count=Count('projects', distinct=True)
    )
    serializer_class = DepartmentSerializer
    permission_classes = [IsDirector|IsCoordinator]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'code']
    
    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        department = self.get_object()
        users = department.utilisateurs.all()
        serializer = UserListSerializer(users, many=True)
        return Response({'status': 'success', 'data': serializer.data})
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        department = self.get_object()
        data = {
            'users': department.utilisateurs.count(),
            'projects': department.projects.count(),
            'by_role': department.utilisateurs.values('role').annotate(count=Count('id')),
            'by_section': department.sections.annotate(
                user_count=Count('utilisateurs')
            ).values('name', 'user_count')
        }
        return Response({'status': 'success', 'data': data})

class SectionViewSet(viewsets.ModelViewSet):
    queryset = Section.objects.all().select_related('department')
    serializer_class = SectionSerializer
    permission_classes = [IsDirector|IsCoordinator|IsDepartmentHead]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['department']
    search_fields = ['name', 'code']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        if user.role == 'responsable_section' and user.section:
            return queryset.filter(id=user.section.id)
        elif user.role == 'coordinateur' and user.department:
            return queryset.filter(department=user.department)
        return queryset
    
    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        section = self.get_object()
        users = section.utilisateurs.all()
        serializer = UserListSerializer(users, many=True)
        return Response({'status': 'success', 'data': serializer.data})

class CompetenceViewSet(viewsets.ModelViewSet):
    queryset = Competence.objects.all()
    serializer_class = CompetenceSerializer
    permission_classes = [IsDirector|IsCoordinator]

class UserActivityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UserActivity.objects.all().select_related('user')
    serializer_class = UserActivitySerializer
    permission_classes = [IsDirector|IsCoordinator]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['user', 'action']
    ordering_fields = ['-timestamp']