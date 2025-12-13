from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'login', 'role', 'is_active', 'created_at']

class UserWithActorSerializer(serializers.ModelSerializer):
    actor = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'login', 'role', 'is_active', 'created_at', 'actor']

    def get_actor(self, obj):
        if hasattr(obj, 'actor'):
            return {
                'id': obj.actor.id,
                'name': obj.actor.name,
                'type': obj.actor.type
            }
        return None
