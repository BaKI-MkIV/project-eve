# wallet_inventory/serializers.py
from rest_framework import serializers
from .models import Inventory, Wallet

class InventoryUpdateSerializer(serializers.Serializer):
    actor_id = serializers.IntegerField()
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField()

class WalletUpdateSerializer(serializers.Serializer):
    actor_id = serializers.IntegerField()
    currency_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=16, decimal_places=2)
