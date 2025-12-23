# economy/models.py
from django.db import models

from actors.models import Actor
from products.models import Product


class Currency(models.Model):
    name = models.CharField(max_length=50, unique=True)
    symbol = models.CharField(max_length=10, blank=True)
    exchange_rate = models.DecimalField(
        max_digits=18, decimal_places=4,
        default=1.0,
        help_text="Относительно базовой валюты"
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class MarketLot(models.Model):
    LOT_TYPE_CHOICES = [
        ('sell', 'Продажа'),
        ('buy', 'Покупка'),
    ]

    STATUS_CHOICES = [
        ('active', 'Активен'),
        ('completed', 'Завершён'),
        ('cancelled', 'Отменён'),
    ]

    actor = models.ForeignKey(
        Actor,
        on_delete=models.CASCADE,
        related_name='market_lots',
        verbose_name="Актёр"
    )
    lot_type = models.CharField("Тип лота", max_length=10, choices=LOT_TYPE_CHOICES)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="Товар")
    quantity = models.PositiveIntegerField("Количество")
    price_per_unit = models.DecimalField("Цена за единицу", max_digits=16, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, verbose_name="Валюта")
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField("Создан", auto_now_add=True)

    class Meta:
        verbose_name = "Рыночный лот"
        verbose_name_plural = "Рыночные лоты"
        indexes = [
            models.Index(fields=['product', 'lot_type', 'price_per_unit', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['currency']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.get_lot_type_display()}] {self.quantity} × {self.product.name} по {self.price_per_unit} {self.currency.symbol} ({self.actor.name})"

    @property
    def total_price(self):
        return self.price_per_unit * self.quantity