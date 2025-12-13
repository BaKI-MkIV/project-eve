# actors/views.py

from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db import transaction

from .models import Actor
from .serializers import ActorSerializer
from ..accounts.permissions import IsMasterUser


class ActorViewSet(viewsets.ModelViewSet):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer

    def get_permissions(self):
        """
        list и retrieve — всем (включая неавторизованных)
        create/update/delete/bulk_create — только мастер
        """
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsMasterUser()]

    def get_queryset(self):
        """
        Ключевой момент:
        - Для list (и поиск/фильтры) — скрываем is_hidden=True от всех, кроме мастера
        - Для retrieve (просмотр по ID) — возвращаем полный queryset (скрытые тоже)
        """
        user = self.request.user
        is_master = user.is_authenticated and getattr(user, 'role', None) == 'master'

        if self.action == 'list':
            # Только для списка и поиска — скрываем скрытых
            if not is_master:
                return Actor.objects.filter(is_hidden=False).order_by('-created_at')
            return Actor.objects.all().order_by('-created_at')

        # Для retrieve, partial_update и т.д. — мастер видит всё, но игрокам тоже даём доступ к скрытым по ID
        if is_master:
            return Actor.objects.all()
        return Actor.objects.all()  # Даже не-мастеру разрешаем retrieve по ID

    def get_serializer_class(self):
        """
        Публичный сериализатор для всех, кроме мастера
        """
        user = self.request.user
        if user.is_authenticated and getattr(user, 'role', None) == 'master':
            return ActorSerializer  # Мастер видит все поля (включая is_hidden, user и т.д.)

        # Публичная версия — только безопасные поля
        class PublicActorSerializer(serializers.ModelSerializer):
            type_display = serializers.CharField(source='get_type_display', read_only=True)

            class Meta:
                model = Actor
                fields = ['name', 'type', 'type_display', 'description', 'is_system']
                # НЕ включаем: is_hidden, user, created_at, updated_at и т.д.

        return PublicActorSerializer

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        # ... (остаётся без изменений, только мастер может)
        if not isinstance(request.data, list):
            return Response({"error": "Expected a list of objects"}, status=status.HTTP_400_BAD_REQUEST)

        serializers = [self.get_serializer(data=item) for item in request.data]

        if all(s.is_valid() for s in serializers):
            with transaction.atomic():
                for serializer in serializers:
                    serializer.save()
            return Response([s.data for s in serializers], status=status.HTTP_201_CREATED)

        errors = [{"index": i, "errors": s.errors} for i, s in enumerate(serializers) if s.errors]
        return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)