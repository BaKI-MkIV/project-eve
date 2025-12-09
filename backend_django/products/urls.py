# products/urls.py
from django.urls import path
from .views import ProductListCreateView, ProductRetrieveUpdateDestroyView, ProductBulkUploadView

urlpatterns = [
    path("products/", ProductListCreateView.as_view(), name="products-list"),
    path("products/<int:pk>/", ProductRetrieveUpdateDestroyView.as_view(), name="products-detail"),
    path("products/bulk/", ProductBulkUploadView.as_view(), name="products-bulk"),
]