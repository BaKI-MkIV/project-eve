# wallet_inventory/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from .models import Inventory, Wallet
from .serializers import InventoryUpdateSerializer, WalletUpdateSerializer
from actors.models import Actor
from products.models import Product
from economy.models import Currency

class InternalPermission(permissions.BasePermission):
    """
    Разрешает доступ только внутренним сервисам/автоматам.
    Например, юзер должен быть staff и role='automat'
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_staff and getattr(request.user, 'role', '') == 'automat'

class InventoryUpdateView(APIView):
    permission_classes = [InternalPermission]

    def post(self, request):
        serializer = InventoryUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        actor = Actor.objects.get(id=serializer.validated_data['actor_id'])
        product = Product.objects.get(id=serializer.validated_data['product_id'])
        quantity = serializer.validated_data['quantity']

        obj, created = Inventory.objects.get_or_create(actor=actor, product=product)
        obj.quantity += quantity
        if obj.quantity <= 0:
            obj.delete()
            return Response({'status': 'deleted'}, status=status.HTTP_200_OK)
        obj.save()
        return Response({'status': 'ok', 'quantity': obj.quantity}, status=status.HTTP_200_OK)


class WalletUpdateView(APIView):
    permission_classes = [InternalPermission]

    def post(self, request):
        serializer = WalletUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        actor = Actor.objects.get(id=serializer.validated_data['actor_id'])
        currency = Currency.objects.get(id=serializer.validated_data['currency_id'])
        amount = serializer.validated_data['amount']

        obj, created = Wallet.objects.get_or_create(actor=actor, currency=currency)
        obj.amount += amount
        if obj.amount < 0:
            obj.amount = 0
        obj.save()
        return Response({'status': 'ok', 'amount': obj.amount}, status=status.HTTP_200_OK)
