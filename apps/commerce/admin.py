from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import ChoicesDropdownFilter, RangeDateTimeFilter, RelatedDropdownFilter

from .models import FavoriteCollection, FavoriteItem, Order


class FavoriteItemInline(TabularInline):
    model = FavoriteItem
    extra = 0


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ("id", "legacy_id", "company", "customer_name", "quantity", "status", "created_at")
    list_filter = (
        ("status", ChoicesDropdownFilter),
        ("company", RelatedDropdownFilter),
        ("product", RelatedDropdownFilter),
        ("created_at", RangeDateTimeFilter),
    )
    search_fields = ("customer_name", "customer_contact", "legacy_id")
    autocomplete_fields = ("product", "company")
    readonly_fields = ("created_at",)
    fieldsets = (
        (None, {"fields": ("legacy_id", "product", "company", "status")}),
        ("Customer", {"fields": ("customer_name", "customer_contact", "quantity")}),
        ("Snapshot", {"fields": ("product_snapshot",), "classes": ("collapse",)}),
        ("Metadata", {"fields": ("created_at",), "classes": ("collapse",)}),
    )


@admin.register(FavoriteCollection)
class FavoriteCollectionAdmin(ModelAdmin):
    list_display = ("email", "updated_at")
    search_fields = ("email",)
    readonly_fields = ("created_at", "updated_at")
    inlines = [FavoriteItemInline]


@admin.register(FavoriteItem)
class FavoriteItemAdmin(ModelAdmin):
    list_display = ("id", "collection", "product", "created_at")
    list_filter = (("collection", RelatedDropdownFilter), ("product", RelatedDropdownFilter))
    search_fields = ("collection__email", "product__legacy_id", "product__company__name")
    autocomplete_fields = ("collection", "product")
    readonly_fields = ("created_at",)
