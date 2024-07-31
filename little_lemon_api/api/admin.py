from django.contrib import admin
from .models import Category, MenuItem, Cart, Order, OrderItem

# Register your models here.


# Enregistrement du modèle Category
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug')  # Champs à afficher dans la liste
    search_fields = ('title',)  # Champs sur lesquels effectuer des recherches

# Enregistrement du modèle MenuItem
@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'featured', 'category')  # Champs à afficher dans la liste
    list_filter = ('category', 'featured')  # Filtres disponibles dans l'interface
    search_fields = ('title',)  # Champs sur lesquels effectuer des recherches

# Enregistrement du modèle Cart
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'menuitem', 'quantity', 'unit_price', 'price')  # Champs à afficher dans la liste
    search_fields = ('user__username', 'menuitem__title')  # Rechercher par utilisateur ou élément de menu

# Enregistrement du modèle Order
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'total', 'date')  # Champs à afficher dans la liste
    list_filter = ('status',)  # Filtres disponibles dans l'interface
    search_fields = ('user__username',)  # Rechercher par utilisateur

# Enregistrement du modèle OrderItem
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'menuitem', 'quantity', 'unit_price', 'price')  # Champs à afficher dans la liste
    search_fields = ('order__user__username', 'menuitem__title')  # Rechercher par commande ou élément de menu
