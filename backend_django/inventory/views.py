from rest_framework import viewsets
from .models import InventoryItem
from .serializers import InventoryItemSerializer

class InventoryItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemSerializer
