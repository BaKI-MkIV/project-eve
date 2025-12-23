from rest_framework import serializers
from .models import Currency, Tag, MarketLot


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ['id', 'name', 'symbol']

class MarketLotSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_description = serializers.CharField(source='product.description', read_only=True, allow_blank=True)
    currency_symbol = serializers.CharField(source='currency.symbol', read_only=True)
    actor_name = serializers.CharField(source='actor.name', read_only=True)
    total_price = serializers.DecimalField( max_digits=18, decimal_places=2, read_only=True)

    # Для создания лота — передаём actor_id от фронта (мастер может любой)
    actor_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = MarketLot
        fields = [
            'id',
            'actor_id',
            'actor_name',
            'lot_type',
            'product',
            'product_name',
            'product_description',
            'quantity',
            'price_per_unit',
            'currency',
            'currency_symbol',
            'total_price',
            'status',
            'created_at',
        ]
        read_only_fields = ['status', 'created_at', 'total_price', 'actor_name', 'product_name', 'currency_symbol']