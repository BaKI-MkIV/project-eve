# actors/views.py

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Q
from rest_framework.response import Response

from .models import Actor
from .serializers import ActorSerializer

class ActorViewSet(viewsets.ModelViewSet):
    queryset = Actor.objects.all().select_related('user')
    serializer_class = ActorSerializer

    def get_permissions(self):
        """
        - list/retrieve — аутентифицированные пользователи
        - create/update/delete — только мастер/админ
        """
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAdminUser()]

    def get_queryset(self):
        qs = Actor.objects.all().select_related('user')

        # Фильтр по type (основной запрос)
        actor_type = self.request.query_params.get('type')
        if actor_type:
            valid_types = [choice[0] for choice in Actor._meta.get_field('type').choices]
            if actor_type in valid_types:
                qs = qs.filter(type=actor_type)
            else:
                qs = qs.none()  # некорректный type — пустой результат

        # Только активные (по умолчанию)
        is_active = self.request.query_params.get('is_active', 'true')
        if is_active.lower() == 'true':
            qs = qs.filter(is_active=True)
        elif is_active.lower() == 'false':
            qs = qs.filter(is_active=False)

        # Показывать системных актёров? (по умолчанию — нет)
        qs = Actor.objects.all().select_related('user')
        if not self.request.user.role == 'master':
            qs = qs.filter(is_system=False)

        # Только игроки (type='player')
        only_players = self.request.query_params.get('only_players')
        if only_players == 'true':
            qs = qs.filter(type='player')

        # Поиск по имени (частичное совпадение)
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(name__icontains=search)

        return qs.order_by('name')  # удобнее, чем по дате

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        actor = request.user.actor  # связь user → actor уже есть
        if not actor:
            return Response({"detail": "У пользователя нет актёра"}, status=404)
        serializer = ActorSerializer(actor)
        return Response(serializer.data)