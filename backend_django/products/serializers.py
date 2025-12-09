from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'product_id', 'name', 'description', 'tags', 'base_price', 'created_at']
        read_only_fields = ['id', 'product_id', 'created_at']

