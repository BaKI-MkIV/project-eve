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


class Transfer(models.Model):
    TYPE_CHOICES = [
        ('direct', 'Мгновенная отправка'),
        ('request', 'Запрос на получение'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('accepted', 'Принят'),
        ('rejected', 'Отклонён'),
        ('cancelled', 'Отменён'),
    ]

    sender = models.ForeignKey(Actor, on_delete=models.CASCADE, related_name='sent_transfers', verbose_name="Отправитель")
    recipient = models.ForeignKey(Actor, on_delete=models.CASCADE, related_name='received_transfers', verbose_name="Получатель")
    transfer_type = models.CharField("Тип передачи", max_length=10, choices=TYPE_CHOICES)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, null=True, blank=True, verbose_name="Предмет")
    quantity = models.PositiveIntegerField("Количество", default=0)
    amount = models.DecimalField("Сумма", max_digits=16, decimal_places=2, default=0)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, null=True, blank=True, verbose_name="Валюта")
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Передача активов"
        verbose_name_plural = "Передачи активов"

    def __str__(self):
        if self.product:
            return f"Передача {self.quantity} {self.product.name} от {self.sender} к {self.recipient}"
        else:
            return f"Передача {self.amount} {self.currency.symbol} от {self.sender} к {self.recipient}"
