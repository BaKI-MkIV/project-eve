# wallet_inventory/serializers.py (полная версия)

from rest_framework import serializers
from .models import Inventory, Wallet
from products.models import Product
from economy.models import Currency
from actors.models import Actor


# ====================
# Для внутренних обновлений (оставляем как есть)
# ====================

class InventoryUpdateSerializer(serializers.Serializer):
    actor_id = serializers.IntegerField(min_value=1)
    product_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField()

    def validate_actor_id(self, value):
        if not Actor.objects.filter(id=value).exists():
            raise serializers.ValidationError("Актёр с таким ID не существует.")
        return value

    def validate_product_id(self, value):
        if not Product.objects.filter(id=value).exists():
            raise serializers.ValidationError("Продукт с таким ID не существует.")
        return value


class WalletUpdateSerializer(serializers.Serializer):
    actor_id = serializers.IntegerField(min_value=1)
    currency_id = serializers.IntegerField(min_value=1)
    amount = serializers.DecimalField(max_digits=16, decimal_places=2)

    def validate_actor_id(self, value):
        if not Actor.objects.filter(id=value).exists():
            raise serializers.ValidationError("Актёр с таким ID не существует.")
        return value

    def validate_currency_id(self, value):
        if not Currency.objects.filter(id=value).exists():
            raise serializers.ValidationError("Валюта с таким ID не существует.")
        return value


# ====================
# Публичные сериализаторы для просмотра
# ====================

class InventoryItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_description = serializers.CharField(source='product.description', read_only=True, allow_blank=True)
    price = serializers.DecimalField(source='product.price', max_digits=18, decimal_places=2, read_only=True, allow_null=True)
    currency_symbol = serializers.CharField(source='product.currency.symbol', read_only=True, allow_null=True)
    is_active = serializers.BooleanField(source='product.is_active', read_only=True)
    is_legal = serializers.BooleanField(source='product.is_legal', read_only=True)

    class Meta:
        model = Inventory
        fields = [
            'product',               # ID продукта (можно скрыть, если не нужно)
            'product_name',
            'product_description',
            'price',
            'currency_symbol',
            'is_active',
            'is_legal',
            'quantity',
        ]


class WalletItemSerializer(serializers.ModelSerializer):
    currency_name = serializers.CharField(source='currency.name', read_only=True)
    currency_symbol = serializers.CharField(source='currency.symbol', read_only=True)

    class Meta:
        model = Wallet
        fields = [
            'currency',              # ID валюты
            'currency_name',
            'currency_symbol',
            'amount',
        ]