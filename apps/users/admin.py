from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.sites import AlreadyRegistered
from django.contrib.auth.models import Permission

from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import ChoicesDropdownFilter, RelatedDropdownFilter
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from .models import User


class PermissionAdmin(ModelAdmin):
    list_display = ("name", "content_type", "codename")
    list_filter = (("content_type", RelatedDropdownFilter),)
    search_fields = ("name", "codename", "content_type__app_label", "content_type__model")
    ordering = ("content_type__app_label", "content_type__model", "codename")


try:
    admin.site.register(Permission, PermissionAdmin)
except AlreadyRegistered:
    pass


@admin.register(User)
class KonglomeratUserAdmin(UserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    fieldsets = UserAdmin.fieldsets + (
        ("Konglomerat", {"fields": ("role", "company", "display_name")}),
    )
    list_display = ("username", "email", "role", "company", "is_active", "is_staff")
    list_filter = (
        ("role", ChoicesDropdownFilter),
        ("company", RelatedDropdownFilter),
        ("is_active", ChoicesDropdownFilter),
        ("is_staff", ChoicesDropdownFilter),
        ("is_superuser", ChoicesDropdownFilter),
        "groups",
    )
    autocomplete_fields = ("company", "groups", "user_permissions")
    search_fields = ("username", "email", "first_name", "last_name", "display_name", "company__name")
