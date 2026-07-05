from rest_framework import serializers

from apps.commerce.models import Order
from core.utils import external_id


class OrderSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    databaseId = serializers.IntegerField(source="id", read_only=True)
    productId = serializers.SerializerMethodField()
    product = serializers.JSONField(source="product_snapshot")
    customer = serializers.SerializerMethodField()
    qty = serializers.IntegerField(source="quantity")
    at = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ("id", "databaseId", "productId", "product", "customer", "qty", "status", "at")

    def get_id(self, obj: Order) -> str:
        return external_id(obj)

    def get_productId(self, obj: Order) -> str:
        return external_id(obj.product)

    def get_customer(self, obj: Order) -> dict[str, str]:
        return {"name": obj.customer_name, "contact": obj.customer_contact}

    def get_at(self, obj: Order) -> str:
        return obj.created_at.isoformat()
