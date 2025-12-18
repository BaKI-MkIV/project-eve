from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from drf_spectacular.generators import SchemaGenerator
from rest_framework.permissions import AllowAny
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator


# ============ ПУБЛИЧНАЯ СХЕМА (только GET) ============

class PublicSchemaGenerator(SchemaGenerator):
    """
    Генератор схемы только для GET-методов
    Использует postprocessing для фильтрации уже сгенерированной схемы
    """

    def get_schema(self, request=None, public=False):
        """Переопределяем генерацию схемы с фильтрацией"""
        schema = super().get_schema(request, public)

        # Фильтруем paths, оставляя только GET
        if 'paths' in schema:
            filtered_paths = {}

            for path, methods in schema['paths'].items():
                filtered_methods = {}

                for method, operation in methods.items():
                    if method.lower() == 'get':
                        filtered_methods[method] = operation

                if filtered_methods:
                    filtered_paths[path] = filtered_methods

            schema['paths'] = filtered_paths

        return schema


class PublicSchemaView(SpectacularAPIView):
    """Публичная схема API (только GET)"""
    permission_classes = [AllowAny]
    generator_class = PublicSchemaGenerator


class PublicDocsView(SpectacularSwaggerView):
    """Публичная документация Swagger"""
    permission_classes = [AllowAny]
    url_name = 'public-schema'


# ============ STAFF СХЕМА (все методы, требует staff) ============

@staff_member_required
def staff_schema_view(request):
    """
    Схема для staff пользователей
    Требует авторизации через стандартную форму Django
    """
    view = SpectacularAPIView.as_view()
    return view(request)


@staff_member_required
def staff_docs_view(request):
    """
    Swagger UI для staff пользователей
    Требует авторизации через стандартную форму Django
    """
    view = SpectacularSwaggerView.as_view(url_name='schema')
    return view(request)