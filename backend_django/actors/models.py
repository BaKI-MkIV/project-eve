# backend_django/actors/models.py
from django.db import models
from django.db.models import Q
from django.conf import settings


class Actor(models.Model):
    """
    Актор — единая сущность, участвующая в сделках.
    Игроки, НПС, банк, торговцы — все акторы.
    """
    name = models.CharField(max_length=255, db_index=True, help_text="Имя актора")
    description = models.TextField(blank=True, help_text="Описание актора")

    # Если это игрок, user должен быть указан
    # Если это системный актор, user = None
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='actors'
    )

    # Активен ли актор (может участвовать в сделках)
    is_active = models.BooleanField(
        default=True,
        help_text="Если False, актор не участвует в новых сделках, не видим игрокам"
    )

    # Системный актор = любой НПС, банк, рынок, налоговая и т.д.
    is_system = models.BooleanField(
        default=False,
        help_text="True для всех акторов, которые не игроки"
    )

    # Тип актора в игровом мире
    type = models.CharField(
        max_length=20,
        choices=[
            ('player', 'Player'),
            ('npc', 'NPC'),
            ('bank', 'Bank'),
            ('merchant', 'Merchant'),
            ('guild', 'Guild'),
            ('organization', 'Organization'),
        ],
        default='npc',
        help_text="Роль актора в мире"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['name', 'type'])]
        constraints = [
            # Игрок должен иметь user
            models.CheckConstraint(
                condition=~Q(type='player') | Q(user__isnull=False),
                name='player_must_have_user'
            ),
            # Системный актор не может быть игроком
            models.CheckConstraint(
                condition=Q(is_system=True, user__isnull=True) | Q(is_system=False, user__isnull=False),
                name='system_or_player_consistency'
            ),
        ]
