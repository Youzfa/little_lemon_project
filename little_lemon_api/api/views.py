from django.shortcuts import render
from rest_framework import viewsets, status
from .models import MenuItem, Category, Order, Cart, OrderItem
from .permissions import IsManager, IsDeliveryCrew, IsCustomer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import MenuItemSerializer, CategorySerializer
from .serializers import UserSerializer, GroupSerializer
from .serializers import OrderSerializer, CartSerializer
from django_filters import rest_framework as django_filters
from django_filters import rest_framework as filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle




# Obtenez le modèle d'utilisateur
User = get_user_model()

class MenuItemFilter(django_filters.FilterSet):
    class Meta:
        model = MenuItem
        fields = {
            'title': ['exact', 'icontains'],  # Recherche par titre
            'price': ['exact', 'gte', 'lte'],  # Filtrage par prix
            'category__slug': ['exact'],  # Filtrage par catégorie
        }

class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    filter_backends = (filters.OrderingFilter, filters.SearchFilter, django_filters.DjangoFilterBackend)
    filterset_class = MenuItemFilter
    search_fields = ['title']  # Permet de rechercher par titre
    ordering_fields = ['price', 'title']  # Champs par lesquels vous pouvez trier
    ordering = ['title']  # Tri par défaut

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            self.permission_classes = [IsManager]  # Seuls les gestionnaires peuvent créer, mettre à jour ou supprimer
        elif self.request.method in ['GET']:
            # Les clients et les livreurs peuvent lire
            self.permission_classes = [IsCustomer | IsDeliveryCrew | IsManager]  # Les gestionnaires peuvent aussi lire
        return super().get_permissions()
    
    def get_queryset(self):
        category_slug = self.request.query_params.get('category')
        if category_slug:
            return self.queryset.filter(category__slug=category_slug)
        return self.queryset


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()  # Assurez-vous que User est correctement importé
    serializer_class = UserSerializer
    permission_classes = [IsManager]

    @action(detail=True, methods=['post'])
    def groups(self, request, pk=None):
        user = self.get_object()
        serializer = GroupSerializer(data=request.data, many=True)
        if serializer.is_valid():
            user.groups.set(serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OrderFilter(django_filters.FilterSet):
    class Meta:
        model = Order
        fields = {
            'user': ['exact'],  # Filtrer par utilisateur
            'status': ['exact'],  # Filtrer par statut
            'date': ['exact', 'gte', 'lte'],  # Filtrer par date
        }

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    
    throttle_classes = [UserRateThrottle, AnonRateThrottle]  # Appliquer le throttling
    
    filter_backends = (filters.OrderingFilter, filters.SearchFilter, django_filters.DjangoFilterBackend)
    filterset_class = OrderFilter
    
    search_fields = ['user__username']  # Permet de rechercher par nom d'utilisateur
    ordering_fields = ['date', 'total']  # Champs par lesquels vous pouvez trier
    ordering = ['date']  # Tri par défaut
    
    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated()]  # Seuls les utilisateurs authentifiés peuvent modifier
        return super().get_permissions()

    def assign_delivery_crew(self, request, pk=None):
        order = self.get_object()
        delivery_crew_id = request.data.get('delivery_crew_id')

        try:
            delivery_crew = User.objects.get(id=delivery_crew_id)
            order.delivery_crew = delivery_crew
            order.save()
            return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "Delivery crew not found."}, status=status.HTTP_404_NOT_FOUND)

    def mark_as_delivered(self, request, pk=None):
        order = self.get_object()
        order.status = True  # Marquer comme livré
        order.save()
        return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)
    
    def create(self, request):
        user = request.user
        cart_items = Cart.objects.filter(user=user)

        if not cart_items.exists():
            return Response({"error": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        total_price = sum(item.price for item in cart_items)
        order = Order.objects.create(user=user, total=total_price, status=False)  # Créez une commande avec le total

        # Créez des éléments de commande à partir des éléments du panier
        for item in cart_items:
            OrderItem.objects.create(order=order, menuitem=item.menuitem, quantity=item.quantity,
                                     unit_price=item.unit_price, price=item.price)

        # Videz le panier après la commande
        cart_items.delete()

        return Response({"message": "Order placed successfully.", "order_id": order.id}, status=status.HTTP_201_CREATED)


class CartViewSet(viewsets.ViewSet):
    def add_to_cart(self, request, user_id):
        user = User.objects.get(id=user_id)
        menuitem_id = request.data.get('menuitem')
        quantity = request.data.get('quantity')

        try:
            menuitem = MenuItem.objects.get(id=menuitem_id)
        except MenuItem.DoesNotExist:
            return Response({"error": "Menu item not found."}, status=status.HTTP_404_NOT_FOUND)

        cart_item, created = Cart.objects.get_or_create(
            user=user,
            menuitem=menuitem,
            defaults={'quantity': quantity, 'unit_price': menuitem.price, 'price': menuitem.price * quantity}
        )

        if not created:
            # Si l'élément est déjà dans le panier, mettez à jour la quantité
            cart_item.quantity += quantity
            cart_item.price = cart_item.unit_price * cart_item.quantity
            cart_item.save()

        return Response(CartSerializer(cart_item).data, status=status.HTTP_201_CREATED)

    def view_cart(self, request, user_id):
        cart_items = Cart.objects.filter(user_id=user_id)
        serializer = CartSerializer(cart_items, many=True)
        return Response(serializer.data)

    def empty_cart(self, request, user_id):
        Cart.objects.filter(user_id=user_id).delete()
        return Response({"message": "Cart emptied successfully."}, status=status.HTTP_204_NO_CONTENT)
