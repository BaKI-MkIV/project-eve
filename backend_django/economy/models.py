# economy/models.py
from django.db import models

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
