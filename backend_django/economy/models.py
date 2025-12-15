# economy/models.py

from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

class Currency(models.Model):
    code = models.CharField(
        max_length=10,
        unique=True,
        help_text="Код валюты, например: GP, SP, CP, PP"
    )
    name = models.CharField(max_length=50)
    precision = models.PositiveSmallIntegerField(
        default=2,
        help_text="Количество знаков после запятой (2 для GP, можно 0 для монет без дробей)"
    )
    order = models.PositiveSmallIntegerField(
        default=100,
        help_text="Порядок в иерархии (меньше = выше: 10=PP, 20=GP, 30=SP, 40=CP)"
    )

    def __str__(self):
        return f"{self.code} — {self.name}"

    class Meta:
        verbose_name = 'Валюта'
        verbose_name_plural = 'Валюты'
        ordering = ['order']


class ActorBalance(models.Model):
    actor = models.ForeignKey('actors.Actor', on_delete=models.CASCADE, related_name='balances')
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    amount = models.DecimalField(
        max_digits=20,
        decimal_places=8,  # Поддержим дробные (0.001 GP и т.д.)
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )

    class Meta:
        unique_together = ('actor', 'currency')
        verbose_name = 'Баланс актора'
        verbose_name_plural = 'Балансы акторов'

    def __str__(self):
        return f"{self.actor.name} — {self.amount} {self.currency.code}"