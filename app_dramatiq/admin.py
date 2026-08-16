from django.contrib import admin

from core.models import Report


@admin.action(description="Enqueue generate_report via Dramatiq")
def enqueue_dramatiq_generate_report(modeladmin, request, queryset):
    from app_dramatiq.tasks import generate_report

    for report in queryset:
        generate_report.send(report.duration_seconds)
