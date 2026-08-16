from django.contrib import admin

from core.models import Report


@admin.action(description="Enqueue generate_report via Chancy")
def enqueue_chancy_generate_report(modeladmin, request, queryset):
    from app_chancy.tasks import generate_report
    from chancy_instance import chancy

    for report in queryset:
        chancy.sync_push(generate_report.job.with_kwargs(n=report.duration_seconds))
