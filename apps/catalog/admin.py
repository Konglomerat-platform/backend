from django.contrib import admin

from .models import Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "legacy_id", "company", "price_label", "created_at")
    list_filter = ("company",)
    search_fields = ("legacy_id", "company__name")
    inlines = [ProductImageInline]
