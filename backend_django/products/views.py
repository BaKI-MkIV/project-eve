# products/views.py
from django.db import transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from .models import Product
from .serializers import ProductSerializer
from .utils import generate_product_id


class ProductListCreateView(ListCreateAPIView):
    queryset = Product.objects.order_by('id')
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]  # у тебя глобально IsAuthenticated, оставляем

    def perform_create(self, serializer):
        # при создании через обычный POST - назначаем product_id
        product = serializer.save()
        if not product.product_id:
            product.product_id = generate_product_id()
            product.save()


class ProductRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]


class ProductBulkUploadView(APIView):
    # разрешаем только админам/стффу
    permission_classes = [IsAdminUser]

    def post(self, request):
        """
        Ожидаем JSON вида:
        1) { "items": [ {...}, {...} ] }
        2) Или сразу массив: [ {...}, {...} ]
        """
        data = request.data
        if isinstance(data, dict) and "items" in data:
            items = data["items"]
        elif isinstance(data, list):
            items = data
        else:
            return Response({"detail": "Неверный формат данных"}, status=status.HTTP_400_BAD_REQUEST)

        if not items:
            return Response({"detail": "items пуст"}, status=status.HTTP_400_BAD_REQUEST)

        created = []
        errors = []

        with transaction.atomic():
            for idx, item in enumerate(items, start=1):
                name = item.get("name")
                base_price = item.get("base_price")
                if not name or base_price is None:
                    errors.append({"index": idx, "error": "name и base_price обязательны"})
                    continue

                product = Product(
                    name=name,
                    description=item.get("description", ""),
                    tags=item.get("tags", []),
                    base_price=base_price
                )
                product.save()
                if not product.product_id:
                    product.product_id = generate_product_id()
                    product.save(update_fields=['product_id'])

                created.append(ProductSerializer(product).data)

            if errors:
                transaction.set_rollback(True)
                return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"created": created}, status=status.HTTP_201_CREATED)

