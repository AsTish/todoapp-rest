"""
URL configuration for todoapp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LogoutView
from django.views.generic import TemplateView
from todolist.views import TaskCharListView, TaskCharDetailView, TaskCharCreateView, TaskCharUpdateView, TaskDeleteAPIView, LoginAPIView, LogoutAPIView, RegisterAPIView

urlpatterns = [
    path('swagger/', TemplateView.as_view(
        template_name='index.html',
        extra_context={'schema_url': 'swagger/openapi_spec.json'}
    ), name='swagger-ui'),

    path('admin/', admin.site.urls),

    path('tasks/', TaskCharListView.as_view(), name='task-list'),
    path('tasks/<uuid:pk>/', TaskCharDetailView.as_view(), name='task-detail'),
    path('tasks/create/', TaskCharCreateView.as_view(), name='task-create'),
    path('tasks/update/<uuid:pk>/', TaskCharUpdateView.as_view(), name='task-update'),
    path('tasks/delete/<uuid:pk>/', TaskDeleteAPIView.as_view(), name='task-delete'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('register/', RegisterAPIView.as_view(), name='register'),
]
