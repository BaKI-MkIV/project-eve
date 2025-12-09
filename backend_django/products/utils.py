from django.db import transaction
from .models import Product

def generate_product_id():
    """
    Берём последний по id (pk) объект и увеличиваем номер.
    Возвращаем строку вида Pr0001.
    """
    last = Product.objects.order_by('-id').first()
    next_number = last.id + 1 if last else 1
    return f"Pr{next_number:04d}"