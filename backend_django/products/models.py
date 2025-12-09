# products/models.py
from django.db import models

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name



class Product(models.Model):
    # автосгенерируемый целочисленный PK оставляем как есть
    # id = models.AutoField(primary_key=True)  # по умолчанию
    product_id = models.CharField(max_length=12, unique=True, blank=True)  # 'Pr0001'
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    tags = models.JSONField(default=list, blank=True)  # если PostgreSQL -> JSONB, иначе TextField
    base_price = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)



    def save(self, *args, **kwargs):
        # если product_id не задан — установим позже (в view/utility) или здесь можно оставить пустым
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product_id or 'Pr?'} — {self.name}"
