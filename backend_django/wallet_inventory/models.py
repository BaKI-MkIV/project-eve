from django.db import models
from actors.models import Actor
from economy.models import Currency
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
