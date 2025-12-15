# actors/serializers.py

from rest_framework import serializers
from .models import Actor

# Полный сериализатор (для мастера)
class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = '__all__'

# Публичный для игроков (только то, что видно)
class PublicActorSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = Actor
        fields = ['id', 'name', 'type', 'type_display', 'description', 'is_system']

# Для обновления игроком (только редактируемые поля)
class UpdateMeActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = ['name', 'description']  # Только это можно менять игроку