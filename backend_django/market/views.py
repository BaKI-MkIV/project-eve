# market/views.py
from decimal import Decimal

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from django.db import transaction
from datetime import timedelta

from .models import MarketOrder, FrozenInventory, FrozenBalance, Trade
from .serializers import MarketOrderListSerializer, MarketOrderCreateSerializer, MarketOrderDetailSerializer
from economy.models import ActorBalance
from inventory.models import InventoryItem

class MarketOrderViewSet(viewsets.ModelViewSet):
    queryset = MarketOrder.objects.filter(status='active').select_related('actor', 'product', 'currency', 'broker')
    permission_classes = [AllowAny]  # Список и детали — всем, создание — авторизованным

    def get_permissions(self):
        if self.action in ['create']:
            return [IsAuthenticated()]
        return [AllowAny()]

    def get_serializer_class(self):
        if self.action == 'list':
            return MarketOrderListSerializer
        if self.action == 'create':
            return MarketOrderCreateSerializer
        return MarketOrderDetailSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        # Фильтры
        product_id = self.request.query_params.get('product')
        order_type = self.request.query_params.get('type')
        if product_id:
            qs = qs.filter(product_id=product_id)
        if order_type in ['buy', 'sell']:
            qs = qs.filter(order_type=order_type)
        # Сортировка по цене
        sort = self.request.query_params.get('sort', '-unit_price')  # по умолчанию дорогие сверху
        return qs.order_by(sort)

    @transaction.atomic
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            actor = request.user.actor

            order = serializer.save(
                actor=actor,
                remaining_quantity=serializer.validated_data['quantity'],
                status='active'
            )

            quantity = serializer.validated_data['quantity']
            total_price = quantity * order.unit_price

            if order.order_type == 'sell':
                # Заморозка предметов
                item = actor.inventory_items.get(product=order.product)
                item.quantity -= quantity
                item.save()
                FrozenInventory.objects.create(order=order, product=order.product, quantity=quantity)

            elif order.order_type == 'buy':
                # Заморозка денег
                balance = actor.balances.get(currency=order.currency)
                balance.amount -= total_price
                balance.save()
                FrozenBalance.objects.create(order=order, currency=order.currency, amount=total_price)

            return Response(MarketOrderDetailSerializer(order).data, status=201)

        return Response(serializer.errors, status=400)


    def retrieve(self, request, pk=None):
        order = self.get_object()
        # Обновляем expired при просмотре
        if order.expires_at < timezone.now() and order.status == 'active':
            order.status = 'expired'
            order.save()
            # Возврат замороженного (пока просто размораживаем)
            self._unfreeze_order(order)
        return Response(MarketOrderDetailSerializer(order).data)

    def _unfreeze_order(self, order):
        if order.order_type == 'sell':
            frozen = FrozenInventory.objects.filter(order=order)
            for f in frozen:
                item, _ = InventoryItem.objects.get_or_create(actor=order.actor, product=f.product)
                item.quantity += f.quantity
                item.save()
                f.delete()
        elif order.order_type == 'buy':
            frozen = FrozenBalance.objects.filter(order=order)
            for f in frozen:
                balance, _ = ActorBalance.objects.get_or_create(actor=order.actor, currency=f.currency)
                balance.amount += f.amount
                balance.save()
                f.delete()


@action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
@transaction.atomic
def execute(self, request, pk=None):
    order = self.get_object()
    if order.status != 'active':
        return Response({"error": "Ордер не активен"}, status=400)

    executor = request.user.actor

    # Определяем роль исполнителя
    if order.order_type == 'sell':
        buyer = executor
        seller = order.actor
        executed_quantity = Decimal(request.data.get('quantity', order.remaining_quantity))
        if executed_quantity > order.remaining_quantity:
            return Response({"error": "Нельзя купить больше, чем осталось"}, status=400)
    elif order.order_type == 'buy':
        seller = executor
        buyer = order.actor
        executed_quantity = Decimal(request.data.get('quantity', order.remaining_quantity))
        if executed_quantity > order.remaining_quantity:
            return Response({"error": "Нельзя продать больше, чем запрошено"}, status=400)
    else:
        return Response({"error": "Неверный тип ордера"}, status=400)

    total_price = executed_quantity * order.unit_price
    broker_fee = total_price * (order.broker_fee_percent / 100)

    # Проверки ресурсов исполнителя
    if order.order_type == 'sell':  # исполнитель покупает → нужны деньги
        try:
            buyer_balance = buyer.balances.get(currency=order.currency)
            if buyer_balance.amount < total_price:
                return Response({"error": "Недостаточно средств для покупки"}, status=400)
        except ActorBalance.DoesNotExist:
            return Response({"error": "Нет баланса в нужной валюте"}, status=400)

    elif order.order_type == 'buy':  # исполнитель продаёт → нужны предметы
        try:
            seller_inventory = seller.inventory_items.get(product=order.product)
            if seller_inventory.quantity < executed_quantity:
                return Response({"error": "Недостаточно предметов для продажи"}, status=400)
        except InventoryItem.DoesNotExist:
            return Response({"error": "Предмета нет в инвентаре"}, status=400)

    # Переводы
    # Деньги: от покупателя к продавцу и брокеру
    buyer_balance.amount -= total_price
    buyer_balance.save()

    seller_balance, _ = seller.balances.get_or_create(currency=order.currency)
    seller_balance.amount += (total_price - broker_fee)
    seller_balance.save()

    broker_balance, _ = order.broker.balances.get_or_create(currency=order.currency)
    broker_balance.amount += broker_fee
    broker_balance.save()

    # Предметы: от продавца к покупателю
    if order.order_type == 'sell':
        frozen = FrozenInventory.objects.get(order=order, product=order.product)
        frozen.quantity -= executed_quantity
        if frozen.quantity == 0:
            frozen.delete()
        else:
            frozen.save()

        # Разморозка остатка не нужна — он остаётся замороженным
        seller_item = seller.inventory_items.get(product=order.product)
        seller_item.quantity -= executed_quantity
        if seller_item.quantity == 0:
            seller_item.delete()
        else:
            seller_item.save()

    else:  # buy order
        executor_item = executor.inventory_items.get(product=order.product)
        executor_item.quantity -= executed_quantity
        if executor_item.quantity == 0:
            executor_item.delete()
        else:
            executor_item.save()

        frozen = FrozenBalance.objects.get(order=order)
        frozen.amount -= total_price
        if frozen.amount == 0:
            frozen.delete()
        else:
            frozen.save()

    buyer_item, _ = buyer.inventory_items.get_or_create(product=order.product)
    buyer_item.quantity += executed_quantity
    buyer_item.save()

    # Обновление ордера
    order.remaining_quantity -= executed_quantity
    if order.remaining_quantity <= 0:
        order.status = 'closed'
        # Разморозка остатка (если был partial)
        if order.order_type == 'sell' and FrozenInventory.objects.filter(order=order).exists():
            remaining_frozen = FrozenInventory.objects.get(order=order)
            seller_item, _ = seller.inventory_items.get_or_create(product=order.product)
            seller_item.quantity += remaining_frozen.quantity
            seller_item.save()
            remaining_frozen.delete()
        elif order.order_type == 'buy' and FrozenBalance.objects.filter(order=order).exists():
            remaining_frozen = FrozenBalance.objects.get(order=order)
            buyer_balance.amount += remaining_frozen.amount
            buyer_balance.save()
            remaining_frozen.delete()
    order.save()

    # Запись в историю
    Trade.objects.create(
        buy_order=order if order.order_type == 'buy' else None,
        sell_order=order if order.order_type == 'sell' else None,
        buyer=buyer,
        seller=seller,
        product=order.product,
        quantity=executed_quantity,
        unit_price=order.unit_price,
        total_price=total_price,
        broker_fee=broker_fee
    )

    return Response({
        "message": "Ордер исполнен",
        "executed_quantity": executed_quantity,
        "total_price": total_price,
        "broker_fee": broker_fee,
        "remaining_quantity": order.remaining_quantity
    })