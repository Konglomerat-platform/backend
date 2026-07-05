from django.contrib import admin

from .models import Conference, ConferenceAttendance, ManagementModule, Report


class ConferenceAttendanceInline(admin.TabularInline):
    model = ConferenceAttendance
    extra = 0


@admin.register(Conference)
class ConferenceAdmin(admin.ModelAdmin):
    list_display = ("id", "legacy_id", "name", "date", "time", "capacity_total")
    search_fields = ("legacy_id", "name")
    inlines = [ConferenceAttendanceInline]


@admin.register(ManagementModule)
class ManagementModuleAdmin(admin.ModelAdmin):
    list_display = ("key", "block_index", "module_index", "enabled", "updated_at")
    list_filter = ("enabled", "block_index")


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("id", "scope", "company", "generated_by", "created_at")
    list_filter = ("scope", "company")
