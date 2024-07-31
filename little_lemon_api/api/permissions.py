from rest_framework import permissions

class IsManager(permissions.BasePermission):
    """
    Permission pour permettre uniquement aux gestionnaires d'effectuer des opérations de création, mise à jour et suppression.
    """

    def has_permission(self, request, view):
        return request.user.groups.filter(name='Manager').exists() #Gestionnaire

class IsDeliveryCrew(permissions.BasePermission):
    """
    Permission pour permettre uniquement aux livreurs d'effectuer certaines opérations.
    """

    def has_permission(self, request, view):
        return request.user.groups.filter(name='Delivery crew').exists() #Équipe de livraison

class IsCustomer(permissions.BasePermission):
    """
    Permission pour permettre uniquement aux clients d'effectuer certaines opérations.
    """

    def has_permission(self, request, view):
        return request.user.groups.filter(name='Customer').exists() #client
