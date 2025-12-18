# actors/admin.py
from django.contrib import admin
from .models import Actor


@admin.register(Actor)
class ActorAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'is_active', 'is_system')
    list_filter = ('type', 'is_system', 'is_active')
    search_fields = ('name', 'description')
