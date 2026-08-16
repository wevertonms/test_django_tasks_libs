from django.contrib import admin

from core.models import Report


@admin.action(description="Enqueue generate_report via Django Tasks (DB)")
def enqueue_tasks_db_generate_report(modeladmin, request, queryset):
    from app_tasks_db.tasks import generate_report

    for report in queryset:
        generate_report.enqueue(report.duration_seconds)
