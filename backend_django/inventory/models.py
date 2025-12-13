from django.db import models

class InventoryItem(models.Model):
    actor = models.ForeignKey('actors.Actor', on_delete=models.CASCADE)
    product = models.ForeignKey('products.Product', on_delete=models.PROTECT)

    quantity = models.DecimalField(max_digits=18, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('actor', 'product')
