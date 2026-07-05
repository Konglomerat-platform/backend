from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import RangeDateFilter, RangeDateTimeFilter, RelatedDropdownFilter

from .models import NewsArticle, NewsImage


class NewsImageInline(TabularInline):
    model = NewsImage
    extra = 0


@admin.register(NewsArticle)
class NewsArticleAdmin(ModelAdmin):
    list_display = ("id", "legacy_id", "publisher_name", "published_on")
    list_filter = (
        ("published_on", RangeDateFilter),
        ("company", RelatedDropdownFilter),
        ("created_at", RangeDateTimeFilter),
    )
    search_fields = ("legacy_id", "publisher_name", "company__name")
    autocomplete_fields = ("company",)
    readonly_fields = ("created_at", "updated_at")
    inlines = [NewsImageInline]
    fieldsets = (
        (None, {"fields": ("legacy_id", "company", "publisher_name", "icon", "published_on")}),
        ("Content", {"fields": ("title_i18n", "summary_i18n", "body_i18n")}),
        ("Metadata", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


@admin.register(NewsImage)
class NewsImageAdmin(ModelAdmin):
    list_display = ("id", "article", "name", "sort_order")
    list_filter = (("article", RelatedDropdownFilter),)
    search_fields = ("name", "article__legacy_id", "article__publisher_name")
    autocomplete_fields = ("article",)
