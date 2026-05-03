from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('projects', views.ProjectViewSet, basename='project')
router.register('tasks', views.TaskViewSet, basename='task')

urlpatterns = [
    path('api/auth/register/', views.RegisterView.as_view(), name='api-register'),
    path('api/auth/login/', views.LoginTokenObtainPairView.as_view(), name='api-login'),
    path('api/dashboard/', views.DashboardView.as_view(), name='api-dashboard'),
    path('api/', include(router.urls)),
    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('logout/', views.logout_page, name='logout'),
    path('', views.dashboard_page, name='dashboard'),
    path('projects/', views.project_list_page, name='project-list'),
    path('tasks/', views.task_list_page, name='task-list'),
]
