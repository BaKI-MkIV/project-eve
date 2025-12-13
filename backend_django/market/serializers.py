from rest_framework import serializers
from .models import MarketOrder, FrozenInventory, FrozenBalance
from products.serializers import ProductSerializer
from actors.serializers import ActorSerializer
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
