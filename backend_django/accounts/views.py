from rest_framework import viewsets
from .models import User
from .serializers import UserSerializer, UserWithActorSerializer

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserWithActorSerializer
