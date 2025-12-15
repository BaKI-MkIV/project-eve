from django.db import models

# market/models.py

class MarketOrder(models.Model):
    ORDER_TYPE = (
        ('buy', 'Buy'),
        ('sell', 'Sell'),
    )

    STATUS = (
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('expired', 'Expired'),
        ('arrested', 'Arrested'),
    )

    actor = models.ForeignKey('actors.Actor', on_delete=models.PROTECT)

    product = models.ForeignKey('products.Product', on_delete=models.PROTECT)

    order_type = models.CharField(max_length=4, choices=ORDER_TYPE)

    quantity = models.DecimalField(max_digits=18, decimal_places=2)
    remaining_quantity = models.DecimalField(max_digits=18, decimal_places=2)

    unit_price = models.DecimalField(max_digits=18, decimal_places=2)
    currency = models.ForeignKey('economy.Currency', on_delete=models.PROTECT)

    broker = models.ForeignKey(
        'actors.Actor',
        on_delete=models.PROTECT,
        related_name='brokered_orders'
    )

    broker_fee_percent = models.DecimalField(
        max_digits=5, decimal_places=2
    )

    expires_at = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS)

    created_at = models.DateTimeField(auto_now_add=True)


class FrozenInventory(models.Model):
    order = models.ForeignKey(MarketOrder, on_delete=models.CASCADE)
    product = models.ForeignKey('products.Product', on_delete=models.PROTECT)

    quantity = models.DecimalField(max_digits=18, decimal_places=2)


class FrozenBalance(models.Model):
    order = models.ForeignKey(MarketOrder, on_delete=models.CASCADE)
    currency = models.ForeignKey('economy.Currency', on_delete=models.PROTECT)

    amount = models.DecimalField(max_digits=18, decimal_places=2)


class Trade(models.Model):
    buy_order = models.ForeignKey(MarketOrder, on_delete=models.PROTECT, null=True, blank=True,
                                  related_name='buy_trades')
    sell_order = models.ForeignKey(MarketOrder, on_delete=models.PROTECT, null=True, blank=True,
                                   related_name='sell_trades')

    buyer = models.ForeignKey('actors.Actor', on_delete=models.PROTECT, related_name='purchases')
    seller = models.ForeignKey('actors.Actor', on_delete=models.PROTECT, related_name='sales')

    product = models.ForeignKey('products.Product', on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=18, decimal_places=2)
    unit_price = models.DecimalField(max_digits=18, decimal_places=2)
    total_price = models.DecimalField(max_digits=20, decimal_places=8)  # quantity * unit_price
    broker_fee = models.DecimalField(max_digits=20, decimal_places=8, default=0)  # комиссия брокеру

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Сделка {self.quantity} {self.product} по {self.unit_price} GP"