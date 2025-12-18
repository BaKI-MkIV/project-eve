from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework.permissions import IsAdminUser

urlpatterns = [

    path('admin/', admin.site.urls),
    path('auth/', include('accounts.urls')),

    path('actors/', include('actors.urls')),
    path('economy/', include('economy.urls')),

    path(
        'tech/schema/',
        SpectacularAPIView.as_view(permission_classes=[IsAdminUser]),
        name='schema'
    ),
    path(
        'tech/docs/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui'
    ),
    path(
        'tech/redoc/',
        SpectacularRedocView.as_view(url_name='schema'),
        name='redoc'
    ),

]