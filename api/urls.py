from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    LoginView, LogoutView, RefreshTokenView, CurrentUserView,
    DashboardStatsView, DashboardActivitiesView, DashboardChartDataView
)
from utilisateurs.views import (
    UserViewSet, PosteViewSet, DepartmentViewSet,
    SectionViewSet, CompetenceViewSet, UserActivityViewSet
)
from taches.views import (
    ProjectViewSet, TaskViewSet, TaskCommentViewSet,
    TaskAttachmentViewSet, NotificationViewSet
)

router = DefaultRouter()

# Utilisateurs
router.register(r'users', UserViewSet, basename='user')
router.register(r'postes', PosteViewSet)
router.register(r'departments', DepartmentViewSet)
router.register(r'sections', SectionViewSet)
router.register(r'competences', CompetenceViewSet)
router.register(r'activities', UserActivityViewSet)

# Tâches et Projets
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'task-comments', TaskCommentViewSet)
router.register(r'task-attachments', TaskAttachmentViewSet)
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    # Authentification
    path('auth/login/', LoginView.as_view(), name='auth_login'),
    path('auth/logout/', LogoutView.as_view(), name='auth_logout'),
    path('auth/refresh/', RefreshTokenView.as_view(), name='auth_refresh'),
    path('auth/me/', CurrentUserView.as_view(), name='auth_me'),
    
    # Dashboard
    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard_stats'),
    path('dashboard/activities/', DashboardActivitiesView.as_view(), name='dashboard_activities'),
    path('dashboard/charts/', DashboardChartDataView.as_view(), name='dashboard_charts'),
    
    # API Router
    path('', include(router.urls)),
]