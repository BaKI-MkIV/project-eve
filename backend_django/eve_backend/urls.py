from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from eve_backend.views import PublicSchemaView, PublicDocsView, staff_schema_view, staff_docs_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('accounts.urls')),
    path('actors/', include('actors.urls')),
    path('economy/', include('economy.urls')),

    # Полная схема для staff (через login/password)
    path('tech/schema/', staff_schema_view, name='schema'),
    path('tech/docs/', staff_docs_view, name='swagger-ui'),
    path(
        'tech/redoc/',
        SpectacularRedocView.as_view(url_name='schema'),
        name='redoc'
    ),

    # Публичная схема (только GET, доступна всем)
    path('public/schema/', PublicSchemaView.as_view(), name='public-schema'),
    path('public/docs/', PublicDocsView.as_view(), name='public-docs'),
]