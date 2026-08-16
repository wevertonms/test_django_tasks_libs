from django.contrib import admin

from core.models import Report


@admin.action(description="Enqueue generate_report via Procrastinate")
def enqueue_procrastinate_generate_report(modeladmin, request, queryset):
    from app_procrastinate.tasks import generate_report

    for report in queryset:
        generate_report.defer(n=report.duration_seconds)
