from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Q
from django.utils import timezone
from import_export.admin import ImportExportModelAdmin
from rangefilter.filters import DateRangeFilter
from .models import Project, Task, TaskComment, TaskAttachment, Notification
from .admin_dashboard import DashboardMetrics

@admin.register(Project)
class ProjectAdmin(ImportExportModelAdmin):
    list_display = ['code', 'name', 'department', 'priority_badge', 
                   'status_badge', 'start_date', 'end_date', 'progress_bar']
    list_filter = ['status', 'priority', 'department', 
                  ('start_date', DateRangeFilter),
                  ('end_date', DateRangeFilter)]
    search_fields = ['name', 'code', 'description']
    filter_horizontal = ['coordinators']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('code', 'name', 'description', 'department')
        }),
        ('Gestion', {
            'fields': ('coordinators', 'priority', 'status')
        }),
        ('Planning', {
            'fields': ('start_date', 'end_date')
        }),
        ('Métadonnées', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )
    
    def priority_badge(self, obj):
        colors = {1: '#6c757d', 2: '#17a2b8', 3: '#ffc107', 4: '#fd7e14', 5: '#dc3545'}
        labels = {1: 'Très basse', 2: 'Basse', 3: 'Moyenne', 4: 'Haute', 5: 'Critique'}
        return format_html(
            '<span style="background-color: {}; padding: 3px 8px; border-radius: 3px; color: white;">{}</span>',
            colors[obj.priority],
            labels[obj.priority]
        )
    priority_badge.short_description = "Priorité"
    
    def status_badge(self, obj):
        colors = {
            'planning': '#6c757d',
            'active': '#28a745',
            'on_hold': '#ffc107',
            'completed': '#17a2b8',
            'cancelled': '#dc3545'
        }
        return format_html(
            '<span style="background-color: {}; padding: 3px 8px; border-radius: 3px; color: white;">{}</span>',
            colors[obj.status],
            obj.get_status_display()
        )
    status_badge.short_description = "Statut"
    
    def progress_bar(self, obj):
        progress = obj.get_progress()
        color = 'success' if progress >= 75 else 'warning' if progress >= 50 else 'info'
        return format_html(
            '<div style="width: 100px; background-color: #e9ecef; border-radius: 3px;">'
            '<div style="width: {}%; background-color: {}; height: 20px; border-radius: 3px; '
            'text-align: center; color: white; font-size: 11px; line-height: 20px;">{}%</div>'
            '</div>',
            progress, 
            '#28a745' if color == 'success' else '#ffc107' if color == 'warning' else '#17a2b8',
            progress
        )
    progress_bar.short_description = "Progression"
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si création
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Task)
class TaskAdmin(ImportExportModelAdmin):
    list_display = ['title', 'project', 'status_badge', 'priority_badge', 
                   'assigned_users', 'due_date', 'is_overdue_badge', 'completion_badge']
    list_filter = ['status', 'priority', 'complexity', 'is_completed',
                  'project', ('due_date', DateRangeFilter)]
    search_fields = ['title', 'description', 'project__name']
    filter_horizontal = ['assigned_to']
    readonly_fields = ['created_at', 'updated_at', 'completed_date']
    
    fieldsets = (
        ('Informations', {
            'fields': ('title', 'description', 'project')
        }),
        ('Assignation', {
            'fields': ('assigned_to', 'created_by')
        }),
        ('Statut', {
            'fields': ('status', 'is_completed', 'completion_percentage')
        }),
        ('Priorité & Complexité', {
            'fields': ('priority', 'complexity')
        }),
        ('Dates', {
            'fields': ('start_date', 'due_date', 'completed_date')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def status_badge(self, obj):
        colors = {
            'todo': '#6c757d',
            'in_progress': '#007bff',
            'review': '#ffc107',
            'done': '#28a745',
            'blocked': '#dc3545'
        }
        return format_html(
            '<span style="background-color: {}; padding: 3px 8px; border-radius: 3px; color: white;">{}</span>',
            colors[obj.status],
            obj.get_status_display()
        )
    status_badge.short_description = "Statut"
    
    def priority_badge(self, obj):
        colors = {1: '#6c757d', 2: '#17a2b8', 3: '#ffc107', 4: '#fd7e14', 5: '#dc3545'}
        return format_html(
            '<span style="background-color: {}; padding: 3px 8px; border-radius: 3px; color: white;">{}</span>',
            colors[obj.priority],
            obj.get_priority_display()
        )
    priority_badge.short_description = "Priorité"
    
    def assigned_users(self, obj):
        users = obj.assigned_to.all()[:3]
        if users:
            return format_html(
                '{} {}',
                ', '.join([f"{u.first_name}" for u in users]),
                f'+ {obj.assigned_to.count() - 3}' if obj.assigned_to.count() > 3 else ''
            )
        return "-"
    assigned_users.short_description = "Assignés"
    
    def is_overdue_badge(self, obj):
        if obj.is_overdue():
            return format_html(
                '<span style="background-color: #dc3545; padding: 3px 8px; border-radius: 3px; color: white;">En retard</span>'
            )
        return format_html(
            '<span style="background-color: #28a745; padding: 3px 8px; border-radius: 3px; color: white;">OK</span>'
        )
    is_overdue_badge.short_description = "État"
    
    def completion_badge(self, obj):
        color = 'success' if obj.completion_percentage >= 75 else 'warning' if obj.completion_percentage >= 50 else 'info'
        return format_html(
            '<div style="width: 60px; background-color: #e9ecef; border-radius: 3px;">'
            '<div style="width: {}%; background-color: {}; height: 20px; border-radius: 3px; '
            'text-align: center; color: white; font-size: 11px; line-height: 20px;">{}%</div>'
            '</div>',
            obj.completion_percentage,
            '#28a745' if color == 'success' else '#ffc107' if color == 'warning' else '#17a2b8',
            obj.completion_percentage
        )
    completion_badge.short_description = "Progression"
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ['task', 'user', 'short_comment', 'created_at']
    list_filter = [('created_at', DateRangeFilter)]
    search_fields = ['task__title', 'comment']
    readonly_fields = ['created_at']
    
    def short_comment(self, obj):
        return obj.comment[:50] + '...' if len(obj.comment) > 50 else obj.comment
    short_comment.short_description = "Commentaire"

@admin.register(TaskAttachment)
class TaskAttachmentAdmin(admin.ModelAdmin):
    list_display = ['filename', 'task', 'user', 'file_size_display', 'uploaded_at']
    list_filter = [('uploaded_at', DateRangeFilter)]
    search_fields = ['filename', 'task__title']
    
    def file_size_display(self, obj):
        if obj.file_size < 1024:
            return f"{obj.file_size} B"
        elif obj.file_size < 1024 * 1024:
            return f"{obj.file_size / 1024:.1f} KB"
        else:
            return f"{obj.file_size / (1024 * 1024):.1f} MB"
    file_size_display.short_description = "Taille"

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', ('created_at', DateRangeFilter)]
    search_fields = ['title', 'message', 'user__email']
    readonly_fields = ['created_at']
    
    actions = ['mark_as_read']
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Marquer comme lues"