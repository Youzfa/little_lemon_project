from django.shortcuts import render
from rest_framework import viewsets
from .models import MenuItem
from .serializers import MenuItemSerializer
from .permissions import IsManager, IsDeliveryCrew, IsCustomer

# Create your views here.

class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            self.permission_classes = [IsManager]  # Seuls les gestionnaires peuvent créer, mettre à jour ou supprimer
        elif self.request.method in ['GET']:
            # Les clients et les livreurs peuvent lire
            self.permission_classes = [IsCustomer | IsDeliveryCrew | IsManager]  # Les gestionnaires peuvent aussi lire
        return super().get_permissions()
