from django.urls import path
from api.views import products_list, products_create, products_delete

urlpatterns = [
    path('products', products_list),
    path('products/', products_list),
    path('products/<int:id>', products_delete),
    path('products/<int:id>/', products_delete),
    path('products', products_create),
    path('products/', products_create),
]
