from rest_framework import viewsets
from .models import MarketOrder
from .serializers import MarketOrderSerializer

class MarketOrderViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MarketOrder.objects.all()
    serializer_class = MarketOrderSerializer
