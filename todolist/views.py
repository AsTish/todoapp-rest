from django.forms.models import BaseModelForm
from django.http import HttpResponse, Http404
from django.shortcuts import redirect, render, redirect, get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy, reverse

from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout

from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate, login
from rest_framework import status
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.authentication import TokenAuthentication


from todolist.models import Task_char 
from todolist.serializers import TaskCharSerializer, RegisterSerializer
from todolist.permissions import IsNotAuthenticated

# Create your views here.

class LoginAPIView(APIView):
    permission_classes = [IsNotAuthenticated]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return Response({"detail": "Successfully logged in"}, status=status.HTTP_200_OK)
        return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"detail": "Successfully logged out"}, status=status.HTTP_200_OK)
    

class RegisterAPIView(APIView):
    permission_classes = [AllowAny]  # Доступ для незарегистрированных пользователей

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"detail": "User successfully registered"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskCharListView(generics.ListAPIView):
    serializer_class = TaskCharSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Фильтрация задач для текущего пользователя
        queryset = Task_char.objects.filter(user=self.request.user)
        
        # Логика поиска
        search_input = self.request.query_params.get('search-area', '')
        if search_input:
            queryset = queryset.filter(title__icontains=search_input)
        
        # Логика сортировки
        sort_by = self.request.query_params.get('sort', 'updated_at')  # По умолчанию сортировка по дате обновления
        order = self.request.query_params.get('order', 'desc')
        if order == 'asc':
            queryset = queryset.order_by('completed', sort_by)
        else:
            queryset = queryset.order_by('completed', f'-{sort_by}')

        return queryset
    
    
class TaskCharDetailView(generics.RetrieveAPIView):
    queryset = Task_char.objects.all()
    serializer_class = TaskCharSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Фильтрация по пользователю, чтобы каждый пользователь мог видеть только свои задачи
        return Task_char.objects.filter(user=self.request.user)
    
    
class TaskCharCreateView(generics.CreateAPIView):
    queryset = Task_char.objects.all()
    serializer_class = TaskCharSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Ассоциация задачи с текущим пользователем
        serializer.save(user=self.request.user)
            

class TaskCharUpdateView(generics.UpdateAPIView):
    queryset = Task_char.objects.all()
    serializer_class = TaskCharSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Получаем задачу текущего пользователя по `id`
        obj = Task_char.objects.get(id=self.kwargs['pk'], user=self.request.user)
        return obj

    def get_queryset(self):
        # Возвращаем только задачи текущего пользователя
        return Task_char.objects.filter(user=self.request.user)
    

class TaskDeleteAPIView(generics.DestroyAPIView):
    queryset = Task_char.objects.all()
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        task = self.get_object()
        if task.user != request.user:
            return Response({"detail": "You do not have permission to delete this task."})
        
        # Удаляем задачу
        task.delete()

        # Возвращаем пустой ответ без статуса
        return Response()  # Пустой Response без явного указания статуса    

    
    
