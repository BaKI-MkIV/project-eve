# wallet_inventory/utils.py

from django.db import transaction
from .models import Inventory, Wallet, FrozenInventory, FrozenWallet



@transaction.atomic
def unfreeze_inventory(actor, product, quantity, reason="manual"):
    """Возвращает замороженные предметы обратно в инвентарь"""
    try:
        frozen = FrozenInventory.objects.get(actor=actor, product=product, reason=reason)
    except FrozenInventory.DoesNotExist:
        raise ValueError(f"Нет замороженных {product.name} по причине '{reason}'")

    if frozen.quantity < quantity:
        raise ValueError(f"Недостаточно заморожено: {frozen.quantity} < {quantity}")

    frozen.quantity -= quantity
    if frozen.quantity <= 0:
        frozen.delete()
    else:
        frozen.save()

    inv, _ = Inventory.objects.get_or_create(actor=actor, product=product)
    inv.quantity += quantity
    inv.save()
    return inv


@transaction.atomic
def freeze_inventory(actor, product, quantity, reason="manual", lot=None):
    """Перемещает quantity предметов из обычного инвентаря в frozen"""
    if not actor.is_system:
        inv, _ = Inventory.objects.get_or_create(actor=actor, product=product)
        if inv.quantity < quantity:
            raise ValueError(f"Недостаточно {product.name} в инвентаре: {inv.quantity} < {quantity}")

        inv.quantity -= quantity
        if inv.quantity <= 0:
            inv.delete()
        else:
            inv.save()

    frozen, _ = FrozenInventory.objects.get_or_create(
        actor=actor, product=product, reason=reason,
        defaults={'quantity': quantity, 'lot': lot}
    )
    if not frozen._state.adding:
        frozen.quantity += quantity
        frozen.save()
    return frozen

@transaction.atomic
def freeze_wallet(actor, currency, amount, reason="manual", lot=None):
    """Замораживает деньги"""
    if not actor.is_system:
        wallet, _ = Wallet.objects.get_or_create(actor=actor, currency=currency, defaults={'amount': 0})
        if wallet.amount < amount:
            raise ValueError(f"Недостаточно средств: {wallet.amount} < {amount}")

        wallet.amount -= amount
        wallet.save()

    frozen, _ = FrozenWallet.objects.get_or_create(
        actor=actor, currency=currency, reason=reason,
        defaults={'amount': amount, 'lot': lot}
    )
    if not frozen._state.adding:
        frozen.amount += amount
        frozen.save()
    return frozen


@transaction.atomic
def unfreeze_wallet(actor, currency, amount, reason="manual"):
    """Размораживает деньги обратно"""
    try:
        frozen = FrozenWallet.objects.get(actor=actor, currency=currency, reason=reason)
    except FrozenWallet.DoesNotExist:
        raise ValueError(f"Нет замороженных средств по причине '{reason}'")

    if frozen.amount < amount:
        raise ValueError(f"Недостаточно заморожено: {frozen.amount} < {amount}")

    frozen.amount -= amount
    if frozen.amount <= 0:
        frozen.delete()
    else:
        frozen.save()

    wallet, _ = Wallet.objects.get_or_create(actor=actor, currency=currency, defaults={'amount': 0})
    wallet.amount += amount
    wallet.save()
    return wallet


@transaction.atomic
def change_inventory_quantity(actor, product, quantity_delta):
    """
    Универсальная функция: добавляет/вычитает quantity_delta (может быть отрицательным).
    Используется и в update_view, и в сделках.
    """
    if quantity_delta == 0:
        return {'status': 'ok', 'quantity': Inventory.objects.filter(actor=actor, product=product).first().quantity or 0}

    obj, created = Inventory.objects.get_or_create(actor=actor, product=product)
    obj.quantity += quantity_delta

    if obj.quantity <= 0:
        obj.delete()
        return {'status': 'deleted'}
    else:
        obj.save()
        return {'status': 'ok', 'quantity': obj.quantity}


@transaction.atomic
def change_wallet_amount(actor, currency, amount_delta):
    """
    Универсальная функция для изменения баланса.
    """
    if amount_delta == 0:
        wallet = Wallet.objects.filter(actor=actor, currency=currency).first()
        return {'status': 'ok', 'amount': wallet.amount if wallet else 0}

    obj, created = Wallet.objects.get_or_create(actor=actor, currency=currency, defaults={'amount': 0})
    obj.amount += amount_delta

    if obj.amount < 0:
        obj.amount = 0

    obj.save()
    return {'status': 'ok', 'amount': obj.amount}