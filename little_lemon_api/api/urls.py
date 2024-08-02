from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MenuItemViewSet, UserViewSet , CategoryViewSet, OrderViewSet, CartViewSet

router = DefaultRouter()
router.register(r'menu-items', MenuItemViewSet)
router.register(r'users', UserViewSet)  # Enregistrement du UserViewSet
router.register(r'categories', CategoryViewSet)
router.register(r'orders', OrderViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('users/<int:user_id>/cart/menu-items/', CartViewSet.as_view({'post': 'add_to_cart'}), name='add-to-cart'),
    path('users/<int:user_id>/cart/', CartViewSet.as_view({'get': 'view_cart', 'delete': 'empty_cart'}), name='view-cart'),
    path('orders/<int:pk>/assign/', OrderViewSet.as_view({'post': 'assign_delivery_crew'}), name='assign-delivery-crew'),
    path('orders/<int:pk>/mark-delivered/', OrderViewSet.as_view({'post': 'mark_as_delivered'}), name='mark-as-delivered'),
]
