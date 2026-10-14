from django.contrib import admin

from core.models import Report


@admin.action(description="Enqueue generate_report via RQ")
def enqueue_rq_generate_report(modeladmin, request, queryset):
    from app_rq.tasks import generate_report

    for report in queryset:
        generate_report.delay(report.duration_seconds)
