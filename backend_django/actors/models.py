from django.db import models


class Actor(models.Model):
    user = models.OneToOneField(
        'accounts.User',
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    name = models.CharField(max_length=255)

    type = models.CharField(
        max_length=20,
        choices=[
            ('player', 'Player'),
            ('npc', 'NPC'),
            ('bank', 'Bank'),
            ('merchant', 'Merchant'),
            ('system', 'System'),
        ]
    )

    is_system = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

