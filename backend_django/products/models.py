from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=255, unique=True, db_index=True)
    price = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    description = models.TextField(blank=True)

    currency = models.ForeignKey(
        'Currency',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        help_text="Валюта, в которой считается цена"
    )

    tags = models.ManyToManyField(
        'Tag',
        blank=True,
        related_name='products',
        help_text="Теги для удобного поиска/фильтрации"
    )

    is_active = models.BooleanField(default=True, help_text="Можно ли взаимодействовать с предметом за пределами своего инвентаря")
    is_legal = models.BooleanField(default=True, help_text="if False - можно передавать, но нельзя выставлять на рынок")  # новые легальные предметы

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name']),
        ]
