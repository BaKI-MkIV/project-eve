from rest_framework import serializers
from .models import Currency, ActorBalance

class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ['id', 'code', 'name', 'precision']

class ActorBalanceSerializer(serializers.ModelSerializer):
    currency = CurrencySerializer(read_only=True)

    class Meta:
        model = ActorBalance
        fields = ['id', 'actor_id', 'currency', 'amount']


class WalletSerializer(serializers.ModelSerializer):
    currency_code = serializers.CharField(source='currency.code')
    currency_name = serializers.CharField(source='currency.name')

    class Meta:
        model = ActorBalance
        fields = ['currency_code', 'currency_name', 'amount']