# economy/views.py

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.shortcuts import get_object_or_404
from decimal import Decimal

from actors.models import Actor
from wallet_inventory.models import FrozenInventory, FrozenWallet
from .models import MarketLot, Transfer, Currency, Tag
from .serializers import MarketLotSerializer, TransferSerializer, CurrencySerializer, TagSerializer
from wallet_inventory.utils import (
    freeze_inventory, unfreeze_inventory,
    freeze_wallet, unfreeze_wallet
)
from wallet_inventory.utils import change_inventory_quantity, change_wallet_amount

class CurrencyViewSet(viewsets.ModelViewSet):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]  # или IsAuthenticated, если мастерам можно создавать

# ---------------- Tag ----------------
class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


class MarketLotViewSet(viewsets.ModelViewSet):
    queryset = MarketLot.objects.filter(status='active').select_related('actor', 'product', 'currency')
    serializer_class = MarketLotSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = MarketLot.objects.filter(status='active').select_related('actor', 'product', 'currency')

        product_id = self.request.query_params.get('product')
        lot_type = self.request.query_params.get('lot_type')
        tag_id = self.request.query_params.get('tag')  # <-- новое
        tag_name = self.request.query_params.get('tag_name')  # <-- опционально по имени

        if product_id:
            qs = qs.filter(product_id=product_id)
        if lot_type in ['sell', 'buy']:
            qs = qs.filter(lot_type=lot_type)
        if tag_id:
            qs = qs.filter(product__tags__id=tag_id)
        if tag_name:
            qs = qs.filter(product__tags__name__iexact=tag_name)  # или contains

        return qs.distinct()

    def perform_create(self, serializer):
        user = self.request.user
        actor_id = self.request.data.get('actor_id')
        if not actor_id:
            return Response({"error": "actor_id обязателен"}, status=status.HTTP_400_BAD_REQUEST)

        actor = get_object_or_404(Actor, id=actor_id)

        # Проверка прав: игрок — только свой актор, мастер — любой
        if user.role == 'player' and (not actor.user or actor.user != user):
            return Response({"error": "Можно создавать лоты только от своего актора"}, status=status.HTTP_403_FORBIDDEN)

        lot = serializer.save()
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

    @action(detail=False, methods=['post'], url_path='bulk_create', permission_classes=[IsAuthenticated])
    def bulk_create(self, request):
        user = request.user

        if user.role != 'master':
            return Response({"error": "Только мастер может загружать лоты bulk"}, status=403)

        lots_data = request.data.get('lots')
        if not lots_data or not isinstance(lots_data, list):
            return Response({"error": "Ожидается список лотов в поле 'lots'"}, status=400)

        created_lots = []
        errors = []

        with transaction.atomic():
            for i, lot_data in enumerate(lots_data):
                actor_id = lot_data.get('actor_id')
                if not actor_id:
                    errors.append({"index": i, "error": "actor_id обязателен"})
                    continue

                serializer = MarketLotSerializer(data=lot_data)
                if serializer.is_valid():
                    lot = serializer.save()
                    reason = f"lot:{lot.id}"

                    try:
                        if lot.lot_type == 'sell':
                            freeze_inventory(
                                actor=lot.actor,
                                product=lot.product,
                                quantity=lot.quantity,
                                reason=reason,
                                lot=lot
                            )
                        else:  # buy
                            total = lot.total_price
                            freeze_wallet(
                                actor=lot.actor,
                                currency=lot.currency,
                                amount=total,
                                reason=reason,
                                lot=lot
                            )
                        created_lots.append(serializer.data)
                    except ValueError as e:
                        # если не хватает ресурсов — удаляем лот
                        lot.delete()
                        errors.append({"index": i, "error": str(e)})
                else:
                    errors.append({"index": i, "error": serializer.errors})

        return Response({
            "created": created_lots,
            "errors": errors
        })

class TransferViewSet(viewsets.ModelViewSet):
    queryset = Transfer.objects.all().select_related('sender', 'recipient', 'product', 'currency')
    serializer_class = TransferSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Игрок видит только свои (отправленные или полученные)
        if user.role == 'player':
            actor = user.actor
            if actor:
                return self.queryset.filter(sender=actor) | self.queryset.filter(recipient=actor)
        # Мастер видит все
        return self.queryset

    # Убрали perform_create — вся логика теперь в сериализаторе

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        transfer = self.get_object()
        user = request.user

        # Только получатель может принять
        if user.role == 'player' and (not transfer.recipient.user or transfer.recipient.user != user):
            return Response({"error": "Можно принять только свой запрос"}, status=403)

        if transfer.status != 'pending' or transfer.transfer_type != 'request':
            return Response({"error": "Нельзя принять этот перевод"}, status=400)

        reason = f"transfer:{transfer.id}"

        with transaction.atomic():
            if transfer.product:
                # Отдаём предмет от получателя отправителю
                change_inventory_quantity(transfer.recipient, transfer.product, -transfer.quantity)
                change_inventory_quantity(transfer.sender, transfer.product, transfer.quantity)
                # Размораживаем (если было заморожено)
                unfreeze_inventory(transfer.recipient, transfer.product, transfer.quantity, reason)
            else:
                change_wallet_amount(transfer.recipient, transfer.currency, -transfer.amount)
                change_wallet_amount(transfer.sender, transfer.currency, transfer.amount)
                unfreeze_wallet(transfer.recipient, transfer.currency, transfer.amount, reason)

            transfer.status = 'accepted'
            transfer.save()

        return Response({"status": "accepted"})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        transfer = self.get_object()
        user = request.user

        if user.role == 'player' and (not transfer.recipient.user or transfer.recipient.user != user):
            return Response({"error": "Можно отклонить только свой запрос"}, status=403)

        if transfer.status != 'pending':
            return Response({"error": "Нельзя отклонить"}, status=400)

        reason = f"transfer:{transfer.id}"

        with transaction.atomic():
            if transfer.transfer_type == 'request':
                if transfer.product:
                    unfreeze_inventory(transfer.recipient, transfer.product, transfer.quantity, reason)
                else:
                    unfreeze_wallet(transfer.recipient, transfer.currency, transfer.amount, reason)

            transfer.status = 'rejected'
            transfer.save()

        return Response({"status": "rejected"})

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        transfer = self.get_object()
        user = request.user

        if user.role == 'player' and (not transfer.sender.user or transfer.sender.user != user):
            return Response({"error": "Можно отменить только свой перевод"}, status=403)

        if transfer.status != 'pending':
            return Response({"error": "Нельзя отменить"}, status=400)

        reason = f"transfer:{transfer.id}"

        with transaction.atomic():
            if transfer.transfer_type == 'request':
                if transfer.product:
                    unfreeze_inventory(transfer.recipient, transfer.product, transfer.quantity, reason)
                else:
                    unfreeze_wallet(transfer.recipient, transfer.currency, transfer.amount, reason)

            transfer.status = 'cancelled'
            transfer.save()

        return Response({"status": "cancelled"})