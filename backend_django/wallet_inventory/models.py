from django.db import models
from actors.models import Actor
from economy.models import Currency, MarketLot
from products.models import Product

class Inventory(models.Model):
    actor = models.ForeignKey(
        Actor,
        on_delete=models.CASCADE,
        related_name='inventory_items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='owners'
    )
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('actor', 'product')

    def __str__(self):
        return f'{self.actor.name} - {self.product.name} x{self.quantity}'


class Wallet(models.Model):
    actor = models.ForeignKey(
        Actor,
        on_delete=models.CASCADE,
        related_name='wallets'
    )
    currency = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        related_name='holders'
    )
    amount = models.DecimalField(max_digits=16, decimal_places=2, default=0)

    class Meta:
        unique_together = ('actor', 'currency')

    def __str__(self):
        return f'{self.actor.name} - {self.amount} {self.currency.symbol}'


class FrozenInventory(models.Model):
    """
    Замороженные предметы в escrow (например, выставлены на продажу)
    """
    lot = models.ForeignKey(
        MarketLot,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='frozen_inventory_items',
        verbose_name="Привязанный лот"
    )
    actor = models.ForeignKey(
        Actor,
        on_delete=models.CASCADE,
        related_name='frozen_inventory_items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='frozen_owners'
    )
    quantity = models.PositiveIntegerField(default=1)
    reason = models.CharField(max_length=100, blank=True)  # например, "lot:42"
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('actor', 'product', 'reason')
        indexes = [
            models.Index(fields=['actor']),
            models.Index(fields=['product']),
            models.Index(fields=['lot']),
            models.Index(fields=['reason']),
        ]

    def __str__(self):
        lot_str = f" (лот {self.lot.id})" if self.lot else ""
        return f"[FROZEN] {self.actor.name} - {self.product.name} x{self.quantity}{lot_str} ({self.reason})"


class FrozenWallet(models.Model):
    """
    Замороженные деньги в escrow
    """
    lot = models.ForeignKey(
        MarketLot,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='frozen_wallets',
        verbose_name="Привязанный лот"
    )
    actor = models.ForeignKey(
        Actor,
        on_delete=models.CASCADE,
        related_name='frozen_wallets'
    )
    currency = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        related_name='frozen_holders'
    )
    amount = models.DecimalField(max_digits=16, decimal_places=2)
    reason = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('actor', 'currency', 'reason')
        indexes = [
            models.Index(fields=['actor']),
            models.Index(fields=['currency']),
            models.Index(fields=['lot']),
            models.Index(fields=['reason']),
        ]

    def __str__(self):
        lot_str = f" (лот {self.lot.id})" if self.lot else ""
        return f"[FROZEN] {self.actor.name} - {self.amount} {self.currency.symbol}{lot_str} ({self.reason})"