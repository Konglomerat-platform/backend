from rest_framework import status
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.commerce.api.serializers import OrderSerializer
from apps.commerce.services import create_order, favorite_ids_for_email, orders_for_user, replace_favorites


class OrderViewSet(ListModelMixin, CreateModelMixin, GenericViewSet):
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return orders_for_user(self.request.user)

    def create(self, request, *args, **kwargs):
        order = create_order(request.data)
        return Response(self.get_serializer(order).data, status=status.HTTP_201_CREATED)


class FavoritesViewSet(GenericViewSet):
    permission_classes = [AllowAny]

    def list(self, request):
        ids = favorite_ids_for_email(str(request.query_params.get("email", "")))
        return Response({"ids": ids})

    def replace(self, request):
        ids = request.data.get("ids") if isinstance(request.data.get("ids"), list) else []
        saved = replace_favorites(str(request.data.get("email", "")), ids)
        return Response({"ids": saved})
