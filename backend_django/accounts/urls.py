from django.urls import path
from .views import MyTokenObtainPairView, MeView, LogoutView, update_profile, MeActorViewSet, MeWalletView, \
    MeInventoryView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', MeView.as_view(), name='me'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('me/update/', update_profile, name='update_profile'),
    path('me/actor/', MeActorViewSet.as_view({
            'get': 'retrieve',       # GET для просмотра
            'patch': 'partial_update'  # PATCH для обновления
        }), name='me_actor'),
    path('me/wallet/', MeWalletView.as_view(), name='me_wallet'),
    path('me/inventory/', MeInventoryView.as_view(), name='me_inventory'),
]