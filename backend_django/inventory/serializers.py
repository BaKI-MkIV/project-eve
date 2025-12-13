from rest_framework import serializers
from .models import InventoryItem
from products.serializers import ProductSerializer

class InventoryItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = InventoryItem
        fields = ['id', 'actor_id', 'product', 'quantity', 'created_at']
