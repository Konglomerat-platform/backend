from django.contrib import admin

from .models import NewsArticle, NewsImage


class NewsImageInline(admin.TabularInline):
    model = NewsImage
    extra = 0


@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ("id", "legacy_id", "publisher_name", "published_on")
    list_filter = ("published_on", "company")
    search_fields = ("legacy_id", "publisher_name")
    inlines = [NewsImageInline]
