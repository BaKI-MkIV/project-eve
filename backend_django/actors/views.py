from rest_framework import viewsets
from .models import Actor
from .serializers import ActorSerializer

class ActorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer
