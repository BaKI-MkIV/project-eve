from rest_framework import viewsets
from .models import Currency, ActorBalance
from .serializers import CurrencySerializer, ActorBalanceSerializer

class CurrencyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer

class ActorBalanceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ActorBalance.objects.all()
    serializer_class = ActorBalanceSerializer
