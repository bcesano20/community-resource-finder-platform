from django.contrib import admin

from core.models import Resource


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "zone", "phone")
    list_filter = ("category", "zone")
    search_fields = ("name", "address", "description")
