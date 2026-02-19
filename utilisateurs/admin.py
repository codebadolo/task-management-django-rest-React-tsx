from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from import_export.admin import ImportExportModelAdmin
from rangefilter.filters import DateRangeFilter
from .models import User, Poste, Department, Section, Competence, UserActivity

@admin.register(Poste)
class PosteAdmin(ImportExportModelAdmin):
    list_display = ['titre', 'code', 'categorie', 'niveau_hierarchique', 
                   'peut_gerer_equipe', 'est_actif', 'colored_tag']
    list_filter = ['categorie', 'est_actif', 'peut_gerer_equipe']
    search_fields = ['titre', 'code', 'description']
    ordering = ['-niveau_hierarchique', 'titre']
    
    def colored_tag(self, obj):
        return format_html(
            '<span style="background-color: {}; padding: 3px 8px; border-radius: 3px; color: white;">{}</span>',
            obj.color,
            obj.titre
        )
    colored_tag.short_description = "Aperçu"

@admin.register(Department)
class DepartmentAdmin(ImportExportModelAdmin):
    list_display = ['name', 'code', 'user_count', 'project_count', 'colored_tag']
    search_fields = ['name', 'code']
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            user_count=Count('utilisateurs', distinct=True),
            project_count=Count('projects', distinct=True)
        )
    
    def user_count(self, obj):
        return obj.user_count
    user_count.short_description = "Utilisateurs"
    
    def project_count(self, obj):
        return obj.project_count
    project_count.short_description = "Projets"
    
    def colored_tag(self, obj):
        return format_html(
            '<span style="background-color: {}; padding: 3px 8px; border-radius: 3px; color: white;">{}</span>',
            obj.color,
            obj.name
        )
    colored_tag.short_description = "Aperçu"

@admin.register(Section)
class SectionAdmin(ImportExportModelAdmin):
    list_display = ['name', 'code', 'department', 'responsable', 'user_count']
    list_filter = ['department', 'responsable']
    search_fields = ['name', 'code', 'department__name']
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            user_count=Count('utilisateurs')
        )
    
    def user_count(self, obj):
        return obj.user_count
    user_count.short_description = "Utilisateurs"

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'get_full_name', 'role', 'poste', 'department', 
                   'section', 'is_active', 'last_login', 'avatar_preview']
    list_filter = ['role', 'is_active', 'department', 'section', 'poste']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['email']
    
    fieldsets = (
        ('Authentification', {
            'fields': ('email', 'password')
        }),
        ('Informations personnelles', {
            'fields': ('first_name', 'last_name', 'profile_photo', 'date_naissance')
        }),
        ('Informations professionnelles', {
            'fields': ('role', 'poste', 'department', 'section', 'date_embauche')
        }),
        ('Compétences', {
            'fields': ('competences',)
        }),
        ('Contact', {
            'fields': ('phone', 'phone_pro', 'adresse', 'ville', 'code_postal', 'pays')
        }),
        ('Préférences', {
            'fields': ('notification_email', 'notification_desktop', 'theme_preference', 'langue')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Métadonnées', {
            'fields': ('last_active', 'created_by', 'date_joined')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ['last_active', 'date_joined']
    
    def avatar_preview(self, obj):
        if obj.profile_photo:
            return format_html(
                '<img src="{}" style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover;" />',
                obj.profile_photo.url
            )
        initials = obj.get_initials()
        colors = ['#3B7FBD', '#F9B572', '#6C9E4F', '#A94442', '#8E6C88']
        color = colors[hash(obj.email) % len(colors)]
        return format_html(
            '<div style="width: 40px; height: 40px; border-radius: 50%; background-color: {}; '
            'display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">{}</div>',
            color, initials
        )
    avatar_preview.short_description = "Avatar"

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'ip_address', 'timestamp']
    list_filter = ['action', ('timestamp', DateRangeFilter)]
    search_fields = ['user__email', 'action']
    readonly_fields = ['user', 'action', 'ip_address', 'timestamp']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False