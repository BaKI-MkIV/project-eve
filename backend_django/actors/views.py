# actors/views.py
from rest_framework import viewsets
from .models import Actor
from .serializers import ActorSerializer

class ActorViewSet(viewsets.ModelViewSet):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer
