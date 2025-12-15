from django.db import transaction
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from actors.models import Actor
from inventory.models import InventoryItem
from .models import Currency, ActorBalance
from .serializers import CurrencySerializer, ActorBalanceSerializer


class CurrencyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer

class ActorBalanceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ActorBalance.objects.all()
    serializer_class = ActorBalanceSerializer
