from django.contrib import admin

from .models import FavoriteCollection, FavoriteItem, Order


class FavoriteItemInline(admin.TabularInline):
    model = FavoriteItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "legacy_id", "company", "customer_name", "quantity", "status", "created_at")
    list_filter = ("status", "company")
    search_fields = ("customer_name", "customer_contact", "legacy_id")


@admin.register(FavoriteCollection)
class FavoriteCollectionAdmin(admin.ModelAdmin):
    list_display = ("email", "updated_at")
    search_fields = ("email",)
    inlines = [FavoriteItemInline]
