from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOwnerOrAdmin(BasePermission):
    """
    Permite editar/eliminar una subasta solo si el usuario es el propietario
    o es administrador. Cualquiera puede consultar (GET).
    """

    def has_object_permission(self, request, view, obj):
        # Permitir acceso de lectura a cualquier usuario (GET, HEAD, OPTIONS)
        if request.method in SAFE_METHODS:
            return True
        # Permitir si el usuario es el creador o es administrador
        return obj.auctioneer == request.user or request.user.is_staff

class IsAuthenticatedOrReadOnly(BasePermission):
    """
    Permite solo lectura para usuarios no autenticados.
    """
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user and request.user.is_authenticated

class IsAdminOrReadOnly(BasePermission):
    """
    Permite solo lectura a todos, y escritura solo a administradores.
    """
    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS or 
            (request.user and request.user.is_staff)
        )