from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MenuItemViewSet  # vue de MenuItem

# urlpatterns = [
#     path('menu-items/', MenuItemViewSet.as_view(), name='menu-items'),

# ]

router = DefaultRouter()
router.register(r'menu-items', MenuItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

