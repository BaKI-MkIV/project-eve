from rest_framework import serializers
from economy.models import Currency, Tag
from economy.serializers import CurrencySerializer, TagSerializer
from products.models import Product


class ProductSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    currency = CurrencySerializer(read_only=True)

    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        write_only=True,
        many=True,
        required=False,  # явно укажем, хотя по умолчанию для many=True это False
    )

    currency_id = serializers.PrimaryKeyRelatedField(
        queryset=Currency.objects.all(),
        write_only=True,
        required=False,   # можно не передавать
        allow_null=True,  # можно передать null
    )

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'price', 'description', 'is_active', 'is_legal',
            'tags', 'tag_ids', 'currency', 'currency_id',
            'created_at', 'updated_at'
        ]

    def create(self, validated_data):
        tag_ids = validated_data.pop('tag_ids', [])
        product = Product.objects.create(**validated_data)
        if tag_ids:  # set([]) очистит все теги, так что проверяем
            product.tags.set(tag_ids)
        return product

    def update(self, instance, validated_data):
        tag_ids = validated_data.pop('tag_ids', None)

        # Обновляем обычные поля (включая currency через currency_id)
        instance = super().update(instance, validated_data)

        if tag_ids is not None:
            instance.tags.set(tag_ids)

        return instance