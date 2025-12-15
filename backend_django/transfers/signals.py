# transfers/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models import TransferRequest
from economy.models import ActorBalance
from inventory.models import InventoryItem
from decimal import Decimal

@receiver(post_save, sender=ActorBalance)
def auto_transfer_money(sender, instance, **kwargs):
    if kwargs.get('created', False):  # Игнор при создании
        return

    requests = TransferRequest.objects.filter(
        from_actor=instance.actor,
        currency=instance.currency,
        type='money',
        is_auto=True,
        status='auto_pending'
    )

    for req in requests:
        available = instance.amount
        needed = req.requested_amount - (req.accepted_amount or Decimal('0'))

        transfer_amount = min(available, needed)
        if transfer_amount > 0:
            with transaction.atomic():
                instance.amount -= transfer_amount
                instance.save()
                to_balance, _ = ActorBalance.objects.get_or_create(actor=req.to_actor, currency=req.currency)
                to_balance.amount += transfer_amount
                to_balance.save()

                req.accepted_amount = (req.accepted_amount or Decimal('0')) + transfer_amount
                if req.accepted_amount >= req.requested_amount:
                    req.status = 'accepted_full'
                else:
                    req.status = 'accepted_partial'
                req.save()

@receiver(post_save, sender=InventoryItem)
def auto_transfer_item(sender, instance, **kwargs):
    if kwargs.get('created', False):
        return

    requests = TransferRequest.objects.filter(
        from_actor=instance.actor,
        product=instance.product,
        type='item',
        is_auto=True,
        status='auto_pending'
    )

    for req in requests:
        available = instance.quantity
        needed = req.requested_amount - (req.accepted_amount or Decimal('0'))

        transfer_quantity = min(available, needed)
        if transfer_quantity > 0:
            with transaction.atomic():
                instance.quantity -= transfer_quantity
                if instance.quantity == 0:
                    instance.delete()
                else:
                    instance.save()

                to_item, _ = InventoryItem.objects.get_or_create(actor=req.to_actor, product=req.product)
                to_item.quantity += transfer_quantity
                to_item.save()

                req.accepted_amount = (req.accepted_amount or Decimal('0')) + transfer_quantity
                if req.accepted_amount >= req.requested_amount:
                    req.status = 'accepted_full'
                else:
                    req.status = 'accepted_partial'
                req.save()