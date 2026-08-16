from django.contrib import admin

from core.models import Report


@admin.action(description="Enqueue generate_report via Huey")
def enqueue_huey_generate_report(modeladmin, request, queryset):
    from app_huey.tasks import generate_report

    for report in queryset:
        generate_report(report.duration_seconds)
