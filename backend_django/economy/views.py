# economy/views.py

from django.db import transaction
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from accounts.permissions import IsMasterUser
from actors.models import Actor
from .models import Currency, ActorBalance
from .serializers import CurrencySerializer, ActorBalanceSerializer, WalletSerializer  # Убедись, что WalletSerializer импортирован


class CurrencyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    permission_classes = [IsAuthenticated]  # Опционально, если хочешь ограничить


class ActorBalanceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ActorBalance.objects.all()
    serializer_class = WalletSerializer  # Используем WalletSerializer для красивого вывода (currency_code, amount и т.д.)
    permission_classes = [IsMasterUser]  # Только мастер может видеть балансы других
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['actor']  # ?actor=1

    def get_queryset(self):
        """
        Мастер может видеть баланс любого актора через ?actor=id
        Обычный игрок — только свой (но он использует /auth/me/wallet/, а не этот эндпоинт)
        """
        qs = super().get_queryset()

        # Если передан actor_id — фильтруем (только мастер может это делать)
        actor_id = self.request.query_params.get('actor')
        if actor_id:
            try:
                actor = Actor.objects.get(id=actor_id)
                qs = qs.filter(actor=actor)
            except (Actor.DoesNotExist, ValueError):
                pass  # Игнорируем неверный ID

        return qs.select_related('currency')