# products/models.py
from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255, unique=True, db_index=True)
    description = models.TextField(blank=True)

    price = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    # Вместо ForeignKey(Currency, ...) используем строку
    currency = models.ForeignKey(
        'economy.Currency',  # <-- строка!
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    is_active = models.BooleanField(default=True)
    is_legal = models.BooleanField(default=True)

    # Вместо ManyToManyField('economy.Tag', ...) используем строку
    tags = models.ManyToManyField('economy.Tag', blank=True, related_name='products')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['name'])]