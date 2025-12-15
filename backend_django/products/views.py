# views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction

from .models import Product
from .serializers import ProductSerializer
from accounts.permissions import IsMasterUser


class ProductViewSet(viewsets.ModelViewSet):

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsMasterUser]

    # Кастомное действие: массовое создание
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """
        POST /api/products/bulk_create/
        Тело: массив объектов Product
        """
        if not isinstance(request.data, list):
            return Response(
                {"error": "Expected a list of objects"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializers = [self.get_serializer(data=item) for item in request.data]

        if all(s.is_valid() for s in serializers):
            with transaction.atomic():
                for serializer in serializers:
                    serializer.save()
            return Response(
                [s.data for s in serializers],
                status=status.HTTP_201_CREATED
            )
        else:
            # Более удобный формат ошибок: с индексом объекта
            errors = [
                {"index": i, "errors": s.errors}
                for i, s in enumerate(serializers)
                if s.errors
            ]
            return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)