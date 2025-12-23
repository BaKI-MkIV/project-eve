from django.db import transaction
from wallet_inventory.utils import (
    unfreeze_inventory,
    unfreeze_wallet,
    change_inventory_quantity,
    change_wallet_amount
)
from .models import Transfer

def accept_transfer(transfer: Transfer):
    """
    Принятие запроса на передачу активов.
    """
    if transfer.status != 'pending' or transfer.transfer_type != 'request':
        raise ValueError("Можно принять только pending-запрос")

    reason = f"transfer:{transfer.id}"

    with transaction.atomic():
        if transfer.product:
            unfreeze_inventory(
                actor=transfer.recipient,
                product=transfer.product,
                quantity=transfer.quantity,
                reason=reason,
            )
            change_inventory_quantity(
                actor=transfer.sender,
                product=transfer.product,
                delta=-transfer.quantity
            )
        else:
            unfreeze_wallet(
                actor=transfer.recipient,
                currency=transfer.currency,
                amount=transfer.amount,
                reason=reason,
            )
            change_wallet_amount(
                actor=transfer.sender,
                currency=transfer.currency,
                delta=-transfer.amount
            )

        transfer.status = 'accepted'
        transfer.save(update_fields=['status'])


def reject_transfer(transfer: Transfer):
    """
    Отклонение запроса на передачу активов.
    """
    if transfer.status != 'pending' or transfer.transfer_type != 'request':
        raise ValueError("Можно отклонить только pending-запрос")

    reason = f"transfer:{transfer.id}"

    with transaction.atomic():
        if transfer.product:
            unfreeze_inventory(
                actor=transfer.recipient,
                product=transfer.product,
                quantity=transfer.quantity,
                reason=reason,
            )
        else:
            unfreeze_wallet(
                actor=transfer.recipient,
                currency=transfer.currency,
                amount=transfer.amount,
                reason=reason,
            )

        transfer.status = 'rejected'
        transfer.save(update_fields=['status'])
