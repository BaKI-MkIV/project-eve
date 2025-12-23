from rest_framework import viewsets, permissions

from wallet_inventory.models import FrozenWallet, FrozenInventory
from .models import Currency, Tag
from .serializers import CurrencySerializer, TagSerializer


# ---------------- Currency ----------------
class CurrencyViewSet(viewsets.ModelViewSet):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

# ---------------- Tag ----------------
class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

# economy/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.shortcuts import get_object_or_404
from decimal import Decimal

from actors.models import Actor
from .models import MarketLot
from .serializers import MarketLotSerializer
from wallet_inventory.utils import (
    freeze_inventory, unfreeze_inventory,
    freeze_wallet, unfreeze_wallet
)
from wallet_inventory.utils import change_inventory_quantity, change_wallet_amount

class MarketLotViewSet(viewsets.ModelViewSet):
    queryset = MarketLot.objects.filter(status='active').select_related('actor', 'product', 'currency')
    serializer_class = MarketLotSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = MarketLot.objects.filter(status='active').select_related('actor', 'product', 'currency')
        product_id = self.request.query_params.get('product')
        lot_type = self.request.query_params.get('lot_type')
        if product_id:
            qs = qs.filter(product_id=product_id)
        if lot_type in ['sell', 'buy']:
            qs = qs.filter(lot_type=lot_type)
        return qs.order_by('price_per_unit' if lot_type == 'sell' else '-price_per_unit')

    def perform_create(self, serializer):
        user = self.request.user
        actor_id = self.request.data.get('actor_id')
        if not actor_id:
            return Response({"error": "actor_id обязателен"}, status=status.HTTP_400_BAD_REQUEST)

        actor = get_object_or_404(Actor, id=actor_id)

        # Проверка прав: игрок — только свой актор, мастер — любой
        if user.role == 'player' and (not actor.user or actor.user != user):
            return Response({"error": "Можно создавать лоты только от своего актора"}, status=status.HTTP_403_FORBIDDEN)

        lot = serializer.save(actor=actor)
        reason = f"lot:{lot.id}"

        with transaction.atomic():
            try:
                if lot.lot_type == 'sell':
                    # Замораживаем предметы + привязываем к лоту
                    freeze_inventory(
                        actor=actor,
                        product=lot.product,
                        quantity=lot.quantity,
                        reason=reason,
                        lot=lot
                    )
                else:  # buy
                    total = lot.total_price
                    freeze_wallet(
                        actor=actor,
                        currency=lot.currency,
                        amount=total,
                        reason=reason,
                        lot=lot
                    )

                # Пытаемся мгновенно найти и исполнить матчинг
                self._try_execute_match(lot)

            except ValueError as e:
                # Если не хватило активов — откатываем всё
                self._unfreeze_lot(lot, reason)
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def _try_execute_match(self, lot):
        """Ищет и исполняет мгновенную сделку"""
        if lot.lot_type == 'sell':
            match = MarketLot.objects.filter(
                status='active',
                lot_type='buy',
                product=lot.product,
                currency=lot.currency,
                price_per_unit__gte=lot.price_per_unit,
                quantity=lot.quantity
            ).order_by('-price_per_unit').first()
        else:
            match = MarketLot.objects.filter(
                status='active',
                lot_type='sell',
                product=lot.product,
                currency=lot.currency,
                price_per_unit__lte=lot.price_per_unit,
                quantity=lot.quantity
            ).order_by('price_per_unit').first()

        if match:
            with transaction.atomic():
                self._execute_trade(lot, match)

    def _execute_trade(self, lot1, lot2):
        sell_lot = lot1 if lot1.lot_type == 'sell' else lot2
        buy_lot = lot2 if lot2.lot_type == 'buy' else lot1

        seller = sell_lot.actor
        buyer = buy_lot.actor
        product = sell_lot.product
        quantity = sell_lot.quantity
        price_per_unit = sell_lot.price_per_unit  # Цена продавца
        total = Decimal(price_per_unit) * quantity
        currency = sell_lot.currency

        # Передаём активы
        change_inventory_quantity(buyer, product, quantity)  # +quantity покупателю
        change_wallet_amount(seller, currency, total)  # +total продавцу

        # Удаляем замороженные записи (по lot)
        FrozenInventory.objects.filter(lot=sell_lot).delete()
        FrozenWallet.objects.filter(lot=buy_lot).delete()

        # Завершаем лоты
        lot1.status = 'completed'
        lot1.save()
        lot2.status = 'completed'
        lot2.save()

    def _unfreeze_lot(self, lot, reason):
        """Размораживает активы при ошибке или отмене"""
        if lot.lot_type == 'sell':
            unfreeze_inventory(lot.actor, lot.product, lot.quantity, reason)
        else:
            unfreeze_wallet(lot.actor, lot.currency, lot.total_price, reason)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        lot = self.get_object()
        user = request.user

        if user.role == 'player' and (not lot.actor.user or lot.actor.user != user):
            return Response({"error": "Можно отменить только свой лот"}, status=status.HTTP_403_FORBIDDEN)
        # master может отменить любой

        if lot.status != 'active':
            return Response({"error": "Лот уже не активен"}, status=status.HTTP_400_BAD_REQUEST)

        reason = f"lot:{lot.id}"
        with transaction.atomic():
            self._unfreeze_lot(lot, reason)
            lot.status = 'cancelled'
            lot.save()

        return Response({"status": "cancelled"})