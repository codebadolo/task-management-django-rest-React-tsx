from rest_framework import serializers
from .models import User, Poste, Department, Section, Competence, UserActivity

class PosteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poste
        fields = '__all__'

class DepartmentSerializer(serializers.ModelSerializer):
    user_count = serializers.SerializerMethodField()
    project_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = '__all__'
    
    def get_user_count(self, obj):
        return obj.utilisateurs.count()
    
    def get_project_count(self, obj):
        return obj.projects.count()

class SectionSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    user_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Section
        fields = '__all__'
    
    def get_user_count(self, obj):
        return obj.utilisateurs.count()

class CompetenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competence
        fields = '__all__'

class UserListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    department_name = serializers.CharField(source='department.name', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)
    poste_titre = serializers.CharField(source='poste.titre', read_only=True)
    avatar_url = serializers.SerializerMethodField()
    initials = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'initials', 'avatar_url', 'role', 'poste', 'poste_titre',
            'department', 'department_name', 'section', 'section_name',
            'phone', 'ville', 'is_active', 'last_login', 'date_joined'
        ]
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_initials(self, obj):
        return obj.get_initials()
    
    def get_avatar_url(self, obj):
        return obj.get_avatar_url()

class UserDetailSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    department_name = serializers.CharField(source='department.name', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)
    poste_details = PosteSerializer(source='poste', read_only=True)
    competences_details = CompetenceSerializer(source='competences', many=True, read_only=True)
    permissions = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ['id', 'email', 'date_joined', 'last_active', 'created_by']
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_permissions(self, obj):
        return {
            'can_manage_team': obj.can_manage_team(),
            'can_create_projects': obj.can_create_projects(),
            'can_validate_tasks': obj.can_validate_tasks(),
        }

class UserCreateUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = [
            'email', 'password', 'first_name', 'last_name', 'role',
            'poste', 'department', 'section', 'phone', 'phone_pro',
            'date_naissance', 'adresse', 'ville', 'code_postal', 'pays',
            'competences', 'is_active', 'notification_email', 'notification_desktop'
        ]
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = super().create(validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

class UserActivitySerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = UserActivity
        fields = '__all__'