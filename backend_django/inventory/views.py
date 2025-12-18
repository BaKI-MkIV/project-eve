from rest_framework import viewsets

from django_filters.rest_framework import DjangoFilterBackend
from accounts.permissions import IsMasterUser
from .models import InventoryItem
from .serializers import InventoryItemSerializer, InventorySerializer


class InventoryItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = InventoryItem.objects.all()
    serializer_class = InventorySerializer
    permission_classes = [IsMasterUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['actor']

    def get_queryset(self):
        qs = super().get_queryset()
        actor_id = self.request.query_params.get('actor')
        if actor_id:
            try:
                qs = qs.filter(actor_id=actor_id)
            except ValueError:
                pass
        return qs.select_related('product')