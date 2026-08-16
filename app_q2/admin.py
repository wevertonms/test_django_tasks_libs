from django.contrib import admin


@admin.action(description="Enqueue generate_report via Django-Q2")
def enqueue_q2_generate_report(modeladmin, request, queryset):
    from django_q.tasks import async_task

    for report in queryset:
        async_task("app_q2.tasks.generate_report", report.duration_seconds)
