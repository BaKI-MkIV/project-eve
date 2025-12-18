# transfers/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from .models import TransferRequest
from .serializers import CreateTransferRequestSerializer, TransferRequestSerializer, RespondTransferRequestSerializer
from economy.models import ActorBalance
from inventory.models import InventoryItem
from decimal import Decimal

class TransferRequestViewSet(viewsets.ModelViewSet):
    queryset = TransferRequest.objects.all()
    serializer_class = TransferRequestSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Отправитель запроса — to_actor = актор пользователя
        req = serializer.save(to_actor=self.request.user.actor)

        # Если is_auto — пытаемся перевести сразу
        if req.is_auto:
            self._attempt_auto_transfer(req)

    def _attempt_auto_transfer(self, req):
        with transaction.atomic():
            amount = req.requested_amount
            if req.type == 'money':
                try:
                    from_balance = ActorBalance.objects.get(actor=req.from_actor, currency=req.currency)
                    if from_balance.amount >= amount:
                        from_balance.amount -= amount
                        from_balance.save()
                        to_balance, _ = ActorBalance.objects.get_or_create(actor=req.to_actor, currency=req.currency)
                        to_balance.amount += amount
                        to_balance.save()
                        req.status = 'accepted_full'
                        req.accepted_amount = amount
                    else:
                        req.status = 'auto_pending'
                        return Response({"error": "Недостаточно средств для немедленного перевода"}, status=400)
                except ActorBalance.DoesNotExist:
                    req.status = 'auto_pending'
                    return Response({"error": "Нет баланса для немедленного перевода"}, status=400)
            elif req.type == 'item':
                try:
                    from_item = InventoryItem.objects.get(actor=req.from_actor, product=req.product)
                    if from_item.quantity >= amount:
                        from_item.quantity -= amount
                        if from_item.quantity == 0:
                            from_item.delete()
                        else:
                            from_item.save()
                        to_item, _ = InventoryItem.objects.get_or_create(actor=req.to_actor, product=req.product)
                        to_item.quantity += amount
                        to_item.save()
                        req.status = 'accepted_full'
                        req.accepted_amount = amount
                    else:
                        req.status = 'auto_pending'
                        return Response({"error": "Недостаточно предметов для немедленного перевода"}, status=400)
                except InventoryItem.DoesNotExist:
                    req.status = 'auto_pending'
                    return Response({"error": "Нет предмета для немедленного перевода"}, status=400)

            req.save()

    @action(detail=False, methods=['get'])
    def incoming(self, request):
        actor = request.user.actor
        requests = self.queryset.filter(from_actor=actor, status__in=['pending', 'auto_pending'])
        serializer = self.get_serializer(requests, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def respond(self, request, pk=None):
        req = self.get_object()
        if req.from_actor != request.user.actor:
            return Response({"error": "Не ваш запрос"}, status=403)

        serializer = RespondTransferRequestSerializer(data=request.data)
        if serializer.is_valid():
            action = serializer.validated_data['action']
            amount = serializer.validated_data.get('amount', req.requested_amount)

            if action == 'reject':
                req.status = 'rejected'
                req.save()
                return Response({"message": "Отказано"})

            if amount > req.requested_amount or amount <= 0:
                return Response({"error": "Неверная сумма"}, status=400)

            with transaction.atomic():
                if req.generate and req.from_actor.is_system:
                    # Генерация "из воздуха" — создаём запись, если нет, но не списываем
                    if req.type == 'money':
                        from_balance, _ = ActorBalance.objects.get_or_create(actor=req.from_actor,
                                                                             currency=req.currency)
                        from_balance.amount += amount  # Оседает, если не перевели, но поскольку переводим — баланс остаётся
                    else:
                        from_item, _ = InventoryItem.objects.get_or_create(actor=req.from_actor, product=req.product)
                        from_item.quantity += amount

                # Стандартный перевод (с проверкой и списанием, если не system)
                if req.type == 'money':
                    from_balance = ActorBalance.objects.get(actor=req.from_actor, currency=req.currency)
                    if not req.from_actor.is_system and from_balance.amount < amount:
                        return Response({"error": "Недостаточно средств"}, status=400)
                    if not req.from_actor.is_system:
                        from_balance.amount -= amount
                        from_balance.save()
                    to_balance, _ = ActorBalance.objects.get_or_create(actor=req.to_actor, currency=req.currency)
                    to_balance.amount += amount
                    to_balance.save()
                else:
                    from_item = InventoryItem.objects.get(actor=req.from_actor, product=req.product)
                    if not req.from_actor.is_system and from_item.quantity < amount:
                        return Response({"error": "Недостаточно предметов"}, status=400)
                    if not req.from_actor.is_system:
                        from_item.quantity -= amount
                        if from_item.quantity == 0:
                            from_item.delete()
                        else:
                            from_item.save()
                    to_item, _ = InventoryItem.objects.get_or_create(actor=req.to_actor, product=req.product)
                    to_item.quantity += amount
                    to_item.save()

                req.accepted_amount = amount
                req.status = 'accepted_full' if amount == req.requested_amount else 'accepted_partial'
                req.save()
                return Response({"message": "Принято", "accepted_amount": amount})

        return Response(serializer.errors, status=400)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        req = self.get_object()
        if req.to_actor != request.user.actor:
            return Response({"error": "Не ваш запрос"}, status=403)

        if req.status not in ['pending', 'auto_pending']:
            return Response({"error": "Нельзя отменить"}, status=400)

        req.status = 'cancelled'
        req.save()
        return Response({"message": "Отменено"})