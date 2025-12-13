from django.db import models

# Create your models here.
# economy/models.py

class Currency(models.Model):
    code = models.CharField(max_length=10, unique=True)   # GOLD
    name = models.CharField(max_length=50)
    precision = models.PositiveSmallIntegerField(default=2)


class ActorBalance(models.Model):
    actor = models.ForeignKey('actors.Actor', on_delete=models.CASCADE)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)

    amount = models.DecimalField(max_digits=18, decimal_places=2)

    class Meta:
        unique_together = ('actor', 'currency')
