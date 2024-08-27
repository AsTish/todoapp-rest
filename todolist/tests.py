from django.test import TestCase, Client
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Task_char
import uuid


class TaskListViewTest(TestCase):
    def setUp(self):
        # Создаем тестовый пользователь
        self.user = User.objects.create_user(username='testuser', password='password123')

        # создание задач
        self.tasks = [
            Task_char.objects.create(
                user=self.user,
                title='Test Task 1',
                description='Description for test task 1',
                completed=False
            ),
            Task_char.objects.create(
                user=self.user,
                title='Test Task 2',
                description='Description for test task 2',
                completed=True
            )
        ]

        self.client = Client()
        self.client.login(username='testuser', password='password123')

    def test_task_list_view(self):
        # Получение URL для списка задач
        url = reverse('tasks')  # Имя URL-адреса для TaskList
        response = self.client.get(url)

        # Проверка на статус 200
        self.assertEqual(response.status_code, 200)

        # Проверка контекста
        self.assertIn('tasks', response.context)
        tasks = response.context['tasks']
        for task in self.tasks:
            self.assertIn(task, tasks)
        

class TaskCreateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        
        self.client = Client()
        self.client.login(username='testuser', password='testpass')

    def test_create_task(self):
        url = reverse('task-create')
        
        data = {
            'title': 'New Task',
            'description': 'This is a new task description',
            'completed': False,
            'created_at': timezone.now(),  # Устанавливаем текущую дату и время
        }
        
        # POST-запрос на создание задачи
        response = self.client.post(url, data)
        
        # Проверка успешного создания задачи (перенаправление на success_url)
        self.assertEqual(response.status_code, 302)
        
        # Проверка наличия задачи в бд
        self.assertEqual(Task_char.objects.count(), 1)
        task = Task_char.objects.first()
        
        self.assertEqual(task.title, data['title'])
        self.assertEqual(task.description, data['description'])
        self.assertEqual(task.completed, data['completed'])
        self.assertEqual(task.user, self.user)
        self.assertEqual(task.created_at.replace(microsecond=0), data['created_at'].replace(microsecond=0))    
        # между созданием объекта и добавлением его в базу проходит некоторое время


class TaskDetailViewTest(TestCase):
    def setUp(self):
        # Создаем тестового пользователя
        self.user = User.objects.create_user(username='testuser', password='password123')

        # Создаем задачу
        self.task = Task_char.objects.create(
            user=self.user,
            title='Test Task',
            description='Description for test task',
            completed=False
        )

        # Создаем клиент и логиним пользователя
        self.client = Client()
        self.client.login(username='testuser', password='password123')

    def test_task_detail_view(self):
        # Получение URL
        url = reverse('task', args=[self.task.id])

        # GET-запрос
        response = self.client.get(url)

        # Проверка статуса ответа
        self.assertEqual(response.status_code, 200)

        # Проверка контекста
        self.assertIn('task', response.context)
        self.assertEqual(response.context['task'], self.task)



class TaskUpdateTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')

        self.task = Task_char.objects.create(
            title='Original Title',
            description='Original Description',
            user=self.user
        )
        self.update_url = reverse('task-update', kwargs={'pk': self.task.id})

    def test_update_task_success(self):
        new_data = {
            'title': 'Updated Title',
            'description': 'Updated Description',
            'completed': True
        }

        response = self.client.post(self.update_url, data=new_data)

        # Проверяем, что перенаправление произошло
        self.assertEqual(response.status_code, 302)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, new_data['title'])
        self.assertEqual(self.task.description, new_data['description'])
        self.assertTrue(self.task.completed)

    def test_update_task_not_found(self):
        invalid_id = uuid.uuid4()
        update_url = reverse('task-update', kwargs={'pk': invalid_id})
        response = self.client.post(update_url, data={})

        # Проверка статуса ответа
        self.assertEqual(response.status_code, 404)

class TaskDeleteTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client = Client()
        self.client.login(username='testuser', password='password')

        self.task = Task_char.objects.create(
            title='Test Task',
            description='This is a test task.',
            user=self.user
        )
        self.delete_url = reverse('task-delete', kwargs={'pk': self.task.id})

    def test_delete_task_success(self):
        # Проверка существования задачи
        self.assertEqual(Task_char.objects.count(), 1)

        # Запрос на удаление задачи
        response = self.client.delete(self.delete_url)

        # Проверка статуса ответа
        self.assertEqual(response.status_code, 204)

        # Проверка, что задача была удалена
        self.assertFalse(Task_char.objects.filter(id=self.task.id).exists())

    def test_delete_task_redirect(self):
        # Запрос на удаление задачи с параметрами сортировки
        delete_url_with_params = f"{self.delete_url}?order=asc&sort=updated_at"
        response = self.client.post(delete_url_with_params, follow=True)

        # Проверка перенаправления
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, expected_url=f"{reverse('tasks')}?order=asc&sort=updated_at")

    def test_delete_task_not_found(self):
        # Попытка удалить задачу с несуществующим ID
        invalid_id = uuid.uuid4()
        response = self.client.delete(reverse('task-delete', kwargs={'pk': invalid_id}))

        # Проверка статуса ответа
        self.assertEqual(response.status_code, 404)