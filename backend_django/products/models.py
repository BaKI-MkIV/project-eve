from django.contrib.postgres.fields import ArrayField
from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=255, db_index=True, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    base_price = models.DecimalField(max_digits=18, decimal_places=2)

    tags = ArrayField(
        models.CharField(max_length=50),
        blank=True,
        default=list,  # ← заменим на правильный вариант ниже
        help_text="Список тегов, например: ['smartphone', 'apple', 'new']"
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']  # опционально: новые сначала
        indexes = [
            models.Index(fields=['name']),  # db_index=True уже создаёт, но так явнее
        ]