# wallet_inventory/views.py
from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from actors.models import Actor
from economy.models import Currency, MarketLot
from products.models import Product
from .models import Inventory, Wallet, FrozenWallet, FrozenInventory
from .serializers import InventoryUpdateSerializer, WalletUpdateSerializer, InventoryItemSerializer, \
    WalletItemSerializer, FrozenWalletItemSerializer, FrozenInventoryItemSerializer
from .utils import unfreeze_wallet, freeze_wallet, unfreeze_inventory, freeze_inventory, change_inventory_quantity, \
    change_wallet_amount


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

        result = change_inventory_quantity(actor, product, quantity)

        if result['status'] == 'deleted':
            return Response({'status': 'deleted'}, status=200)
        return Response(result, status=200)


class WalletUpdateView(APIView):
    permission_classes = [InternalPermission]

    def post(self, request):
        serializer = WalletUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        actor = Actor.objects.get(id=serializer.validated_data['actor_id'])
        currency = Currency.objects.get(id=serializer.validated_data['currency_id'])
        amount = serializer.validated_data['amount']

        result = change_wallet_amount(actor, currency, amount)
        return Response(result, status=200)


class ActorInventoryView(APIView):
    permission_classes = [IsAuthenticated]  # или можно AllowAny, если публично

    def get(self, request, actor_id):
        try:
            actor = Actor.objects.get(id=actor_id)
        except Actor.DoesNotExist:
            raise NotFound("Актёр не найден")

        # Опционально: проверка, что пользователь имеет доступ к этому актёру
        # Например, только владелец или мастер
        # if actor.user != request.user and request.user.role != 'master':
        #     raise PermissionDenied("Нет доступа к инвентарю этого актёра")

        inventory = Inventory.objects.filter(actor=actor).select_related('product', 'product__currency')
        serializer = InventoryItemSerializer(inventory, many=True)
        return Response({
            "actor_id": actor.id,
            "actor_name": actor.name,
            "inventory": serializer.data
        })


class ActorWalletView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, actor_id):
        try:
            actor = Actor.objects.get(id=actor_id)
        except Actor.DoesNotExist:
            raise NotFound("Актёр не найден")

        # Та же проверка доступа, если нужно
        # if actor.user != request.user and request.user.role != 'master':
        #     raise PermissionDenied()

        wallets = Wallet.objects.filter(actor=actor).select_related('currency')
        serializer = WalletItemSerializer(wallets, many=True)
        return Response({
            "actor_id": actor.id,
            "actor_name": actor.name,
            "wallet": serializer.data
        })


class ActorFrozenWalletView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, actor_id):
        try:
            actor = Actor.objects.get(id=actor_id)
        except Actor.DoesNotExist:
            raise NotFound("Актёр не найден")

        # Проверка доступа (игрок — только свой, мастер — любой)
        if request.user.role == 'player' and actor.user != request.user:
            return Response({"error": "Нет доступа"}, status=403)
        # master может всё

        frozen_wallets = FrozenWallet.objects.filter(actor=actor).select_related('currency', 'lot')
        serializer = FrozenWalletItemSerializer(frozen_wallets, many=True)

        return Response({
            "actor_id": actor.id,
            "actor_name": actor.name,
            "frozen_wallet": serializer.data
        })


class ActorFrozenInventoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, actor_id):
        try:
            actor = Actor.objects.get(id=actor_id)
        except Actor.DoesNotExist:
            raise NotFound("Актёр не найден")

        if request.user.role == 'player' and actor.user != request.user:
            return Response({"error": "Нет доступа"}, status=403)

        frozen_inventory = FrozenInventory.objects.filter(actor=actor).select_related('product', 'product__currency', 'lot')
        serializer = FrozenInventoryItemSerializer(frozen_inventory, many=True)

        return Response({
            "actor_id": actor.id,
            "actor_name": actor.name,
            "frozen_inventory": serializer.data
        })


class FreezeInventoryView(APIView):
    permission_classes = [InternalPermission]

    def post(self, request):
        actor_id = request.data.get('actor_id')
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)
        reason = request.data.get('reason', 'manual')
        lot_id = request.data.get('lot_id')  # НОВОЕ

        if not all([actor_id, product_id]):
            return Response({'error': 'actor_id и product_id обязательны'}, status=400)

        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError("quantity должен быть > 0")
        except (ValueError, TypeError):
            return Response({'error': 'quantity должен быть положительным целым'}, status=400)

        try:
            actor = get_object_or_404(Actor, id=actor_id)
            product = get_object_or_404(Product, id=product_id)
            lot = get_object_or_404(MarketLot, id=lot_id) if lot_id else None

            frozen = freeze_inventory(
                actor=actor,
                product=product,
                quantity=quantity,
                reason=reason,
                lot=lot
            )

            return Response({
                'status': 'frozen',
                'frozen_id': frozen.id,
                'quantity': frozen.quantity,
                'lot_id': frozen.lot.id if frozen.lot else None,
                'reason': reason
            })
        except ValueError as e:
            return Response({'error': str(e)}, status=400)
        except Exception as e:
            return Response({'error': f'Ошибка: {str(e)}'}, status=500)


class FreezeWalletView(APIView):
    permission_classes = [InternalPermission]

    def post(self, request):
        actor_id = request.data.get('actor_id')
        currency_id = request.data.get('currency_id')
        amount = request.data.get('amount')
        reason = request.data.get('reason', 'manual')
        lot_id = request.data.get('lot_id')  # НОВОЕ

        if not all([actor_id, currency_id, amount]):
            return Response({'error': 'actor_id, currency_id, amount обязательны'}, status=400)

        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError("amount должен быть > 0")
        except (ValueError, TypeError):
            return Response({'error': 'amount должен быть положительным'}, status=400)

        try:
            actor = get_object_or_404(Actor, id=actor_id)
            currency = get_object_or_404(Currency, id=currency_id)
            lot = get_object_or_404(MarketLot, id=lot_id) if lot_id else None

            frozen = freeze_wallet(
                actor=actor,
                currency=currency,
                amount=amount,
                reason=reason,
                lot=lot
            )

            return Response({
                'status': 'frozen',
                'frozen_id': frozen.id,
                'amount': float(frozen.amount),
                'lot_id': frozen.lot.id if frozen.lot else None,
                'reason': reason
            })
        except ValueError as e:
            return Response({'error': str(e)}, status=400)
        except Exception as e:
            return Response({'error': f'Ошибка: {str(e)}'}, status=500)

class UnfreezeInventoryView(APIView):
    permission_classes = [InternalPermission]

    def post(self, request):
        actor_id = request.data.get('actor_id')
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity')
        reason = request.data.get('reason', 'manual')

        if not all([actor_id, product_id, quantity]):
            return Response({'error': 'actor_id, product_id и quantity обязательны'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError("quantity должен быть положительным")
        except (ValueError, TypeError):
            return Response({'error': 'quantity должен быть положительным целым числом'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            actor = get_object_or_404(Actor, id=actor_id)
            product = get_object_or_404(Product, id=product_id)

            unfreeze_inventory(actor=actor, product=product, quantity=quantity, reason=reason)

            return Response({
                'status': 'unfrozen',
                'quantity': quantity,
                'reason': reason
            }, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'Неизвестная ошибка: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UnfreezeWalletView(APIView):
    permission_classes = [InternalPermission]

    def post(self, request):
        actor_id = request.data.get('actor_id')
        currency_id = request.data.get('currency_id')
        amount = request.data.get('amount')
        reason = request.data.get('reason', 'manual')

        if not all([actor_id, currency_id, amount]):
            return Response({'error': 'actor_id, currency_id и amount обязательны'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError("amount должен быть положительным")
        except (ValueError, TypeError):
            return Response({'error': 'amount должен быть положительным числом'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            actor = get_object_or_404(Actor, id=actor_id)
            currency = get_object_or_404(Currency, id=currency_id)

            unfreeze_wallet(actor=actor, currency=currency, amount=amount, reason=reason)

            return Response({
                'status': 'unfrozen',
                'amount': amount,
                'currency_id': currency.id,
                'reason': reason
            }, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'Неизвестная ошибка: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)