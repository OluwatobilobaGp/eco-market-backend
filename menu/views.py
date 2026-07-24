from rest_framework import viewsets

from .models import MenuItem
from .permissions import IsAdminOrReadOnly
from .serializers import MenuItemSerializer


class MenuItemViewSet(viewsets.ModelViewSet):
    """
    GET  /api/menu/           -> list menu items (supports ?search=pizza)
    GET  /api/menu/<id>/      -> retrieve one item
    POST /api/menu/           -> create item (admin only)
    PUT/PATCH /api/menu/<id>/ -> update item (admin only)
    DELETE /api/menu/<id>/    -> delete item (admin only)
    """

    serializer_class = MenuItemSerializer
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ['name', 'description']

    def get_queryset(self):
        queryset = MenuItem.objects.all()
        # Regular users only ever see items that are marked available;
        # admins see everything so they can re-enable hidden items.
        if not (self.request.user and self.request.user.is_staff):
            queryset = queryset.filter(is_available=True)
        return queryset
