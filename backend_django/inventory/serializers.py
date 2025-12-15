from rest_framework import serializers
from .models import InventoryItem
from products.serializers import ProductSerializer

class InventoryItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = InventoryItem
        fields = ['id', 'actor_id', 'product', 'quantity', 'created_at']


class InventorySerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name')
    product_description = serializers.CharField(source='product.description', read_only=True)
    base_price = serializers.DecimalField(source='product.base_price', max_digits=18, decimal_places=2)

    class Meta:
        model = InventoryItem
        fields = ['product_name', 'product_description', 'base_price', 'quantity']