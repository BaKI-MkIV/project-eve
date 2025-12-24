from rest_framework import serializers

from actors.models import Actor
from products.models import Product
from .models import Currency, Tag, MarketLot, Transfer


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

    def create(self, validated_data):
        # Извлекаем actor_id и находим актора
        actor_id = validated_data.pop('actor_id')
        actor = Actor.objects.get(id=actor_id)

        # Создаём лот с actor
        return MarketLot.objects.create(actor=actor, **validated_data)


class TransferSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.name', read_only=True)
    recipient_name = serializers.CharField(source='recipient.name', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True, allow_null=True)
    currency_symbol = serializers.CharField(source='currency.symbol', read_only=True, allow_null=True)
    amount = serializers.DecimalField(max_digits=16, decimal_places=2, allow_null=True, required=False)
    # Для создания — передаём actor_id отправителя
    sender_actor_id = serializers.IntegerField(write_only=True)

    # Изменяем эти поля на PrimaryKeyRelatedField
    recipient = serializers.PrimaryKeyRelatedField(queryset=Actor.objects.all())
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        allow_null=True,
        required=False
    )
    currency = serializers.PrimaryKeyRelatedField(
        queryset=Currency.objects.all(),
        allow_null=True,
        required=False
    )

    class Meta:
        model = Transfer
        fields = [
            'id',
            'sender_actor_id',
            'sender_name',
            'recipient',
            'recipient_name',
            'transfer_type',
            'product',
            'product_name',
            'quantity',
            'amount',
            'currency',
            'currency_symbol',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['status', 'created_at', 'updated_at', 'sender_name', 'recipient_name']

    def validate(self, data):
        """
        Проверяем, что для денежного перевода указаны amount и currency,
        а для перевода предметов - product и quantity
        """
        has_currency = 'currency' in data and data.get('currency') is not None
        has_amount = 'amount' in data and data.get('amount') is not None and data.get('amount', 0) > 0
        has_product = 'product' in data and data.get('product') is not None
        has_quantity = 'quantity' in data and data.get('quantity') is not None and data.get('quantity', 0) > 0

        # Для денежных переводов
        if has_currency and has_amount:
            # Убедимся, что product и quantity не указаны
            if has_product or has_quantity:
                raise serializers.ValidationError(
                    "Для денежного перевода не указывайте product и quantity"
                )
            # Для денежного перевода установим product и quantity в None
            data['product'] = None
            data['quantity'] = None

        # Для переводов предметов
        elif has_product and has_quantity:
            # Убедимся, что amount и currency не указаны
            if has_currency or has_amount:
                raise serializers.ValidationError(
                    "Для перевода предметов не указывайте amount и currency"
                )
            # Для перевода предметов установим amount и currency в None
            data['currency'] = None
            data['amount'] = None

        else:
            raise serializers.ValidationError(
                "Укажите либо валюту и сумму, либо предмет и количество"
            )

        return data

    def create(self, validated_data):
        # Извлекаем sender_actor_id и находим sender
        sender_actor_id = validated_data.pop('sender_actor_id')
        try:
            sender = Actor.objects.get(id=sender_actor_id)
        except Actor.DoesNotExist:
            raise serializers.ValidationError({"sender_actor_id": "Актор с таким ID не существует."})

        # Проверка прав (аналогично вьюшке, но теперь здесь)
        request = self.context.get('request')
        if request and request.user.role != 'master' and request.user.actor_id != sender.id:
            raise serializers.ValidationError("Можно отправлять только от своего актора.")

        # Создаём трансфер
        return Transfer.objects.create(sender=sender, **validated_data)