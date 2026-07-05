from django.contrib import admin

from .models import Notification, NotificationRead


class NotificationReadInline(admin.TabularInline):
    model = NotificationRead
    extra = 0


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "audience", "target_company", "created_at")
    list_filter = ("audience", "target_company")
    inlines = [NotificationReadInline]
