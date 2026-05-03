from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Project, Task

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'role']
        read_only_fields = ['role']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'first_name', 'last_name']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.role = User.Roles.MEMBER
        user.save()
        return user

class ProjectSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True, required=False)
    member_details = UserSerializer(source='members', many=True, read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'members', 'member_details', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError('Project name is required.')
        return value

class TaskSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())
    assigned_to = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.username', read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'deadline', 'project', 'project_name',
            'assigned_to', 'assigned_to_name', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError('Task title is required.')
        return value

    def validate_deadline(self, value):
        if value < timezone.localdate():
            raise serializers.ValidationError('Deadline cannot be in the past.')
        return value

    def validate_assigned_to(self, value):
        if value and value.role != User.Roles.MEMBER:
            raise serializers.ValidationError('Only members may be assigned to tasks.')
        return value

    def validate(self, attrs):
        if self.instance is None and attrs.get('assigned_to') is None:
            raise serializers.ValidationError({'assigned_to': 'Assigned user is required.'})
        return attrs

class DashboardSerializer(serializers.Serializer):
    total_tasks = serializers.IntegerField()
    completed_tasks = serializers.IntegerField()
    pending_tasks = serializers.IntegerField()
    overdue_tasks = serializers.IntegerField()
