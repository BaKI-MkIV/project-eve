from django.db import models
from django.db.models import Q
from django.contrib.postgres.fields import ArrayField  # Если нужны теги, но для Actor опционально


class Actor(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True, help_text="Описание актора, видно всем")  # Опционально, но полезно

    user = models.OneToOneField(
        'accounts.User',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='actor'
    )

    type = models.CharField(
        max_length=20,
        choices=[
            ('player', 'Player'),
            ('npc', 'NPC'),
            ('bank', 'Bank'),
            ('merchant', 'Merchant'),
            ('system', 'System'),
        ],
        default='npc'
    )

    is_system = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_hidden = models.BooleanField(default=False, help_text="Скрыт от игроков")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['name', 'type'])]
        constraints = [
            models.CheckConstraint(
                condition=Q(type='player', user__isnull=False) | ~Q(type='player'),
                name='player_must_have_user'
            )
        ]