# transfers/serializers.py
from decimal import Decimal

from rest_framework import serializers
from .models import TransferRequest
from products.models import Product
from economy.models import Currency

class CreateTransferRequestSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(write_only=True, required=False)  # Для поиска по имени

    class Meta:
        model = TransferRequest
        fields = ['from_actor', 'type', 'currency', 'product', 'product_name', 'requested_amount', 'is_auto']

    def validate(self, attrs):
        if attrs['type'] == 'money':
            if not attrs.get('currency'):
                raise serializers.ValidationError("Для money нужен currency")
        elif attrs['type'] == 'item':
            if 'product_name' in attrs:
                try:
                    attrs['product'] = Product.objects.get(name=attrs.pop('product_name'))
                except Product.DoesNotExist:
                    raise serializers.ValidationError("Продукт не найден по имени")
            if not attrs.get('product'):
                raise serializers.ValidationError("Для item нужен product")

        if attrs.get('is_auto') and not self.context['request'].user.actor.is_system:
            raise serializers.ValidationError("Авто-запросы только для системных акторов")

        return attrs

class TransferRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransferRequest
        fields = '__all__'
        read_only_fields = ['status', 'accepted_amount', 'created_at', 'updated_at']

class RespondTransferRequestSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['accept', 'reject'])
    amount = serializers.DecimalField(max_digits=20, decimal_places=8, required=False, min_value=Decimal('0.00000001'))