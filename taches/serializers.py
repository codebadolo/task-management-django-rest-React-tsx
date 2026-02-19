from rest_framework import serializers
from .models import Project, Task, TaskComment, TaskAttachment, Notification
from utilisateurs.serializers import UserListSerializer

class ProjectListSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    progress = serializers.SerializerMethodField()
    coordinators_list = UserListSerializer(source='coordinators', many=True, read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = Project
        fields = [
            'id', 'code', 'name', 'description', 'department', 'department_name',
            'priority', 'status', 'start_date', 'end_date', 'progress',
            'coordinators', 'coordinators_list', 'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
    
    def get_progress(self, obj):
        return obj.get_progress()

class ProjectDetailSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    coordinators_list = UserListSerializer(source='coordinators', many=True, read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    tasks_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = '__all__'
    
    def get_tasks_summary(self, obj):
        tasks = obj.tasks.all()
        return {
            'total': tasks.count(),
            'todo': tasks.filter(status='todo').count(),
            'in_progress': tasks.filter(status='in_progress').count(),
            'review': tasks.filter(status='review').count(),
            'done': tasks.filter(is_completed=True).count(),
            'blocked': tasks.filter(status='blocked').count(),
        }

class ProjectCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            'code', 'name', 'description', 'department', 'coordinators',
            'priority', 'status', 'start_date', 'end_date'
        ]

class TaskListSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)
    project_code = serializers.CharField(source='project.code', read_only=True)
    assigned_to_list = UserListSerializer(source='assigned_to', many=True, read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    is_overdue = serializers.SerializerMethodField()
    time_remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'project', 'project_name', 'project_code',
            'status', 'priority', 'complexity', 'assigned_to', 'assigned_to_list',
            'created_by', 'created_by_name', 'start_date', 'due_date', 'completed_date',
            'is_completed', 'completion_percentage', 'is_overdue', 'time_remaining',
            'created_at', 'updated_at'
        ]
    
    def get_is_overdue(self, obj):
        return obj.is_overdue()
    
    def get_time_remaining(self, obj):
        return obj.get_time_remaining()

class TaskDetailSerializer(serializers.ModelSerializer):
    project_details = ProjectListSerializer(source='project', read_only=True)
    assigned_to_list = UserListSerializer(source='assigned_to', many=True, read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    comments_count = serializers.SerializerMethodField()
    attachments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = '__all__'
    
    def get_comments_count(self, obj):
        return obj.comments.count()
    
    def get_attachments_count(self, obj):
        return obj.attachments.count()

class TaskCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'project', 'assigned_to',
            'status', 'priority', 'complexity', 'start_date',
            'due_date', 'is_completed', 'completion_percentage'
        ]

class TaskStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Task.STATUS_CHOICES)
    completion_percentage = serializers.IntegerField(min_value=0, max_value=100, required=False)

class TaskCommentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_avatar = serializers.SerializerMethodField()
    
    class Meta:
        model = TaskComment
        fields = ['id', 'task', 'user', 'user_name', 'user_avatar', 'comment', 'created_at']
        read_only_fields = ['user', 'created_at']
    
    def get_user_avatar(self, obj):
        return obj.user.get_avatar_url()

class TaskAttachmentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    file_url = serializers.SerializerMethodField()
    file_size_display = serializers.SerializerMethodField()
    
    class Meta:
        model = TaskAttachment
        fields = [
            'id', 'task', 'user', 'user_name', 'file', 'file_url',
            'filename', 'file_size', 'file_size_display', 'uploaded_at'
        ]
        read_only_fields = ['user', 'filename', 'file_size', 'uploaded_at']
    
    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None
    
    def get_file_size_display(self, obj):
        if obj.file_size < 1024:
            return f"{obj.file_size} B"
        elif obj.file_size < 1024 * 1024:
            return f"{obj.file_size / 1024:.1f} KB"
        else:
            return f"{obj.file_size / (1024 * 1024):.1f} MB"

class NotificationSerializer(serializers.ModelSerializer):
    task_title = serializers.CharField(source='task.title', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'notification_type', 'title', 'message',
            'task', 'task_title', 'project', 'project_name',
            'is_read', 'created_at'
        ]
        read_only_fields = ['created_at']