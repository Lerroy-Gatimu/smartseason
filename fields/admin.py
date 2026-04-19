from django.contrib import admin
from .models import Field, FieldUpdate


class FieldUpdateInline(admin.TabularInline):
    model = FieldUpdate
    extra = 0
    readonly_fields = ('created_at', 'logged_by')


@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    list_display = ('name', 'crop_type', 'current_stage', 'assigned_to', 'planting_date', 'created_at')
    list_filter = ('current_stage', 'assigned_to')
    search_fields = ('name', 'crop_type')
    inlines = [FieldUpdateInline]


@admin.register(FieldUpdate)
class FieldUpdateAdmin(admin.ModelAdmin):
    list_display = ('field', 'logged_by', 'stage_at_update', 'created_at')
    list_filter = ('stage_at_update',)
