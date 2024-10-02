from rest_framework import serializers
from todolist.models import Task_char

class TaskCharSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task_char
        fields = ['id', 'user', 'title', 'description', 'completed', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return data