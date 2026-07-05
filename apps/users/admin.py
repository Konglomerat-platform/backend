from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class KonglomeratUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Konglomerat", {"fields": ("role", "company", "display_name")}),
    )
    list_display = ("username", "email", "role", "company", "is_active", "is_staff")
    list_filter = UserAdmin.list_filter + ("role", "company")
