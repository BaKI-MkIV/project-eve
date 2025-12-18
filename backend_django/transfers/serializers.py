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
        # 1. Проверка типа запроса и обязательных полей
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
                raise serializers.ValidationError("Для item нужен product или product_name")

        # 2. Проверка флага is_auto — только для системных акторов
        if attrs.get('is_auto'):
            # to_actor — это создатель запроса (request.user.actor)
            if not self.context['request'].user.actor.is_system:
                raise serializers.ValidationError("Авто-запросы только для системных акторов")

        # 3. НОВАЯ ПРОВЕРКА: флаг generate — только для системных from_actor
        if attrs.get('generate', False):
            from_actor = attrs.get('from_actor')
            if not from_actor:
                raise serializers.ValidationError("generate=True требует указания from_actor")
            if not from_actor.is_system:
                raise serializers.ValidationError("generate=True разрешён только для системных акторов (from_actor)")

        # 4. Дополнительно: можно запретить generate + is_auto одновременно, если не нужно
        # if attrs.get('generate') and attrs.get('is_auto'):
        #     raise serializers.ValidationError("generate и is_auto нельзя использовать одновременно")

        return attrs

class TransferRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransferRequest
        fields = '__all__'
        read_only_fields = ['status', 'accepted_amount', 'created_at', 'updated_at']

class RespondTransferRequestSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['accept', 'reject'])
    amount = serializers.DecimalField(max_digits=20, decimal_places=8, required=False, min_value=Decimal('0.00000001'))