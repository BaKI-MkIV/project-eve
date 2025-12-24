# actors/serializers.py

from rest_framework import serializers
from .models import Actor

class ActorSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    user_login = serializers.CharField(source='user.login', read_only=True, allow_null=True)
    is_player = serializers.BooleanField(source='type__exact', read_only=True)  # удобный флаг

    class Meta:
        model = Actor
        fields = [
            'id',
            'name',
            'description',
            'user',
            'user_login',           # логин юзера, если есть
            'is_active',
            'is_system',
            'type',
            'type_display',         # "Player", "Merchant" и т.д. вместо кода
            'is_player',            # True только для type='player'
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at', 'user_login', 'type_display', 'is_player']
        extra_kwargs = {
            'user': {'write_only': True},  # скрываем user в ответе, если не нужно
        }