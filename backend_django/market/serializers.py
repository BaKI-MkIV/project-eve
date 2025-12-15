from datetime import timedelta, timezone

from rest_framework import serializers

from economy.models import ActorBalance
from inventory.models import InventoryItem
from .models import MarketOrder, FrozenInventory, FrozenBalance
from products.serializers import ProductSerializer
from actors.serializers import ActorSerializer, PublicActorSerializer
from economy.serializers import CurrencySerializer

class FrozenInventorySerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = FrozenInventory
        fields = ['id', 'product', 'quantity']

class FrozenBalanceSerializer(serializers.ModelSerializer):
    currency = CurrencySerializer(read_only=True)

    class Meta:
        model = FrozenBalance
        fields = ['id', 'currency', 'amount']

class MarketOrderSerializer(serializers.ModelSerializer):
    actor = ActorSerializer(read_only=True)
    product = ProductSerializer(read_only=True)
    broker = ActorSerializer(read_only=True)
    frozen_inventory = FrozenInventorySerializer(many=True, read_only=True, source='frozeninventory_set')
    frozen_balance = FrozenBalanceSerializer(many=True, read_only=True, source='frozenbalance_set')

    class Meta:
        model = MarketOrder
        fields = [
            'id', 'actor', 'product', 'order_type', 'quantity', 'remaining_quantity',
            'unit_price', 'currency', 'broker', 'broker_fee_percent', 'expires_at',
            'status', 'created_at', 'frozen_inventory', 'frozen_balance'
        ]

class MarketOrderListSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name')
    actor_info = PublicActorSerializer(source='actor', read_only=True)  # Продавец/покупатель
    currency_code = serializers.CharField(source='currency.code')

    class Meta:
        model = MarketOrder
        fields = [
            'id', 'order_type', 'product_name', 'quantity', 'remaining_quantity',
            'unit_price', 'currency_code', 'actor_info', 'broker_fee_percent',
            'expires_at', 'status', 'created_at'
        ]

class MarketOrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketOrder
        fields = [
            'order_type', 'product', 'quantity', 'unit_price', 'currency',
            'broker', 'broker_fee_percent', 'expires_at'
        ]

    def validate(self, attrs):
        user = self.context['request'].user
        actor = user.actor

        order_type = attrs['order_type']
        quantity = attrs['quantity']
        product = attrs['product']
        currency = attrs['currency']

        if order_type == 'sell':
            # Проверка инвентаря
            try:
                item = actor.inventory_items.get(product=product)
                if item.quantity < quantity:
                    raise serializers.ValidationError("Недостаточно предметов в инвентаре")
            except InventoryItem.DoesNotExist:
                raise serializers.ValidationError("Предмета нет в инвентаре")

        elif order_type == 'buy':
            # Проверка баланса
            try:
                balance = actor.balances.get(currency=currency)
                total_cost = quantity * attrs['unit_price']
                if balance.amount < total_cost:
                    raise serializers.ValidationError("Недостаточно средств")
            except ActorBalance.DoesNotExist:
                raise serializers.ValidationError("Нет баланса в этой валюте")

        # expires_at — минимум через час, максимум 30 дней (пример)
        if attrs['expires_at'] < timezone.now() + timedelta(hours=1):
            raise serializers.ValidationError("Срок истечения должен быть минимум через час")

        return attrs

class MarketOrderDetailSerializer(serializers.ModelSerializer):
    actor_info = PublicActorSerializer(source='actor')
    product_name = serializers.CharField(source='product.name')
    currency_code = serializers.CharField(source='currency.code')

    class Meta:
        model = MarketOrder
        fields = '__all__'