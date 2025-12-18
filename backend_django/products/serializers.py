from rest_framework import serializers

from economy.models import Currency, Tag
from economy.serializers import CurrencySerializer, TagSerializer
from products.models import Product


class ProductSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    currency = CurrencySerializer(read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), write_only=True, many=True, source='tags'
    )
    currency_id = serializers.PrimaryKeyRelatedField(
        queryset=Currency.objects.all(), write_only=True, source='currency'
    )

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'price', 'description', 'is_active', 'is_legal',
            'tags', 'tag_ids', 'currency', 'currency_id', 'created_at', 'updated_at'
        ]