from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.catalog.api.serializers import ProductSerializer
from apps.catalog.models import Product
from apps.catalog.services import create_product, delete_product, update_product
from core.utils import get_by_external


class ProductViewSet(ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    lookup_value_regex = r"[^/]+"

    def get_queryset(self):
        qs = Product.objects.select_related("company").prefetch_related("images")
        company_name = self.request.query_params.get("company")
        if company_name:
            qs = qs.filter(company__name=company_name)
        return qs

    def get_object(self):
        product = get_by_external(Product, self.kwargs[self.lookup_field])
        if not product:
            raise NotFound()
        self.check_object_permissions(self.request, product)
        return product

    def create(self, request, *args, **kwargs):
        product = create_product(request.user, request.data)
        serializer = self.get_serializer(product)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        product = update_product(request.user, kwargs[self.lookup_field], request.data)
        return Response(self.get_serializer(product).data)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        delete_product(request.user, kwargs[self.lookup_field])
        return Response({"ok": True})
