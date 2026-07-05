from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import RangeDateTimeFilter, RelatedDropdownFilter

from .models import Product, ProductImage


class ProductImageInline(TabularInline):
    model = ProductImage
    extra = 0


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ("id", "legacy_id", "company", "price_label", "created_at")
    list_filter = (("company", RelatedDropdownFilter), ("created_at", RangeDateTimeFilter))
    search_fields = ("legacy_id", "company__name")
    autocomplete_fields = ("company",)
    readonly_fields = ("created_at", "updated_at")
    inlines = [ProductImageInline]
    fieldsets = (
        (None, {"fields": ("legacy_id", "company", "icon")}),
        ("Content", {"fields": ("name_i18n", "description_i18n")}),
        ("Pricing", {"fields": ("price_label", "price_amount", "currency")}),
        ("Metadata", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


@admin.register(ProductImage)
class ProductImageAdmin(ModelAdmin):
    list_display = ("id", "product", "name", "sort_order")
    list_filter = (("product", RelatedDropdownFilter),)
    search_fields = ("name", "product__legacy_id", "product__company__name")
    autocomplete_fields = ("product",)
