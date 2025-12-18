# transfers/models.py

from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

class TransferRequest(models.Model):
    TYPE_CHOICES = (
        ('money', 'Money'),
        ('item', 'Item'),
    )

    STATUS_CHOICES = (
        ('pending', 'Pending'),            # Ждёт ответа
        ('accepted_full', 'Accepted Full'), # Полностью принят
        ('accepted_partial', 'Accepted Partial'), # Частично
        ('rejected', 'Rejected'),          # Отказано
        ('auto_pending', 'Auto Pending'),  # Авто, висит до пополнения
        ('cancelled', 'Cancelled'),        # Отменён отправителем
    )

    from_actor = models.ForeignKey('actors.Actor', on_delete=models.PROTECT, related_name='outgoing_requests')  # Кто должен отправить (получатель запроса)
    to_actor = models.ForeignKey('actors.Actor', on_delete=models.PROTECT, related_name='incoming_requests')    # Кто запрашивает (отправитель запроса, получит)

    type = models.CharField(max_length=5, choices=TYPE_CHOICES)

    currency = models.ForeignKey('economy.Currency', on_delete=models.PROTECT, null=True, blank=True)  # Для money
    product = models.ForeignKey('products.Product', on_delete=models.PROTECT, null=True, blank=True)    # Для item

    requested_amount = models.DecimalField(
        max_digits=20, decimal_places=8,
        validators=[MinValueValidator(Decimal('0.00000001'))],
        help_text="Запрошенная сумма/количество"
    )

    accepted_amount = models.DecimalField(
        max_digits=20, decimal_places=8,
        null=True, blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Принятая сумма/количество (для partial)"
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    is_auto = models.BooleanField(default=False, help_text="Автоматический запрос (только для системных акторов)")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    generate = models.BooleanField(default=False, help_text="Генерировать ресурсы из воздуха для is_system from_actor")

    class Meta:
        verbose_name = 'Запрос на перевод'
        verbose_name_plural = 'Запросы на переводы'
        ordering = ['-created_at']

    def __str__(self):
        return f"Запрос {self.id}: {self.type} от {self.from_actor} к {self.to_actor} ({self.status})"