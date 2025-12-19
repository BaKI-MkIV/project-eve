# accounts/serializers.py
from django.db import transaction
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from actors.models import Actor
from .models import User


class UserSelfSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    actor = serializers.IntegerField(source='actor.id', read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'login',
            'password',
            'role',
            'is_active',
            'actor',
        ]
        read_only_fields = ['id', 'login', 'role', 'is_active', 'actor']

    def update(self, instance, validated_data):
        password = validated_data.get('password')
        if password:
            instance.set_password(password)
            instance.save()
        return instance


class UserMasterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    generated_password = serializers.CharField(read_only=True)

    actor_id = serializers.IntegerField(
        write_only=True,
        required=False,
        allow_null=True
    )
    actor = serializers.IntegerField(source='actor.id', read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'login',
            'password',
            'generated_password',
            'role',
            'is_active',
            'actor',
            'actor_id',
        ]

    @transaction.atomic
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        actor_id = validated_data.pop('actor_id', None)

        user = User.objects.create_user(
            password=password,
            **validated_data
        )

        if password:
            user._plain_password = password

        actor = None
        if actor_id:
            actor = Actor.objects.filter(id=actor_id).first()

        if actor:
            actor.user = user
            actor.type = 'player'
            actor.is_system = False
            actor.save()
        else:
            Actor.objects.create(
                user=user,
                name=user.login,
                type='player',
                is_system=False,
            )

        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        actor_id = validated_data.pop('actor_id', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()

        if actor_id is not None:
            actor = Actor.objects.filter(id=actor_id).first()
            if actor:
                actor.user = instance
                actor.save()

        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if hasattr(instance, '_plain_password'):
            data['generated_password'] = instance._plain_password
        return data


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'login'

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['id'] = user.id
        token['login'] = user.login
        token['role'] = user.role

        return token