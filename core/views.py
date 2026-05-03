from datetime import date
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.db.models import Q
from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, Project, Task
from .serializers import (
    UserSerializer,
    RegisterSerializer,
    ProjectSerializer,
    TaskSerializer,
    DashboardSerializer,
)
from .permissions import IsAdminUser, IsProjectMemberOrAdmin, IsTaskAssignedOrAdmin

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)

class LoginTokenObtainPairView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]
    serializer_class = TokenObtainPairSerializer

class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMemberOrAdmin]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']

    def get_queryset(self):
        user = self.request.user
        if user.role == User.Roles.ADMIN:
            return Project.objects.all()
        return Project.objects.filter(members=user).distinct()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsAdminUser()]
        return super().get_permissions()

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsTaskAssignedOrAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['deadline', 'status', 'created_at']

    def get_queryset(self):
        user = self.request.user
        if user.role == User.Roles.ADMIN:
            return Task.objects.select_related('project', 'assigned_to').all()
        return Task.objects.select_related('project', 'assigned_to').filter(assigned_to=user)

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            return [permissions.IsAuthenticated(), IsAdminUser()]
        return super().get_permissions()

class DashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role == User.Roles.ADMIN:
            tasks = Task.objects.all()
        else:
            tasks = Task.objects.filter(assigned_to=user)

        total = tasks.count()
        completed = tasks.filter(status=Task.Status.DONE).count()
        pending = tasks.exclude(status=Task.Status.DONE).count()
        overdue = tasks.filter(deadline__lt=date.today()).exclude(status=Task.Status.DONE).count()

        serializer = DashboardSerializer({
            'total_tasks': total,
            'completed_tasks': completed,
            'pending_tasks': pending,
            'overdue_tasks': overdue,
        })
        return Response(serializer.data)

def login_page(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, 'Invalid username or password.')
    return render(request, 'auth/login.html')

def register_page(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        if password != password_confirm:
            messages.error(request, 'Passwords do not match.')
        else:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists.')
            else:
                user = User.objects.create_user(username=username, password=password)
                user.role = User.Roles.MEMBER
                user.save()
                login(request, user)
                return redirect('dashboard')
    return render(request, 'auth/register.html')

def logout_page(request):
    logout(request)
    return redirect('login')

def dashboard_page(request):
    if not request.user.is_authenticated:
        return redirect('login')

    user = request.user
    if user.role == User.Roles.ADMIN:
        tasks = Task.objects.all()
    else:
        tasks = Task.objects.filter(assigned_to=user)

    total_tasks = tasks.count()
    completed_tasks = tasks.filter(status=Task.Status.DONE).count()
    pending_tasks = tasks.exclude(status=Task.Status.DONE).count()
    overdue_tasks = tasks.filter(deadline__lt=date.today()).exclude(status=Task.Status.DONE).count()

    context = {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'overdue_tasks': overdue_tasks,
        'tasks': tasks.order_by('deadline')[:10],
    }
    return render(request, 'dashboard.html', context)

def project_list_page(request):
    if not request.user.is_authenticated:
        return redirect('login')

    user = request.user
    if user.role == User.Roles.ADMIN:
        projects = Project.objects.all()
    else:
        projects = Project.objects.filter(members=user)

    return render(request, 'projects.html', {'projects': projects})

def task_list_page(request):
    if not request.user.is_authenticated:
        return redirect('login')

    user = request.user
    status_filter = request.GET.get('status')
    query = request.GET.get('q', '').strip()

    if user.role == User.Roles.ADMIN:
        tasks = Task.objects.select_related('project', 'assigned_to').all()
    else:
        tasks = Task.objects.select_related('project', 'assigned_to').filter(assigned_to=user)

    if status_filter:
        tasks = tasks.filter(status=status_filter)
    if query:
        tasks = tasks.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(project__name__icontains=query))

    return render(request, 'tasks.html', {
        'tasks': tasks.order_by('deadline'),
        'status_filter': status_filter,
        'query': query,
        'status_choices': Task.Status.choices,
    })
