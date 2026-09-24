from django.contrib import admin

from app_dramatiq.admin import enqueue_dramatiq_generate_report as enqueue_dramatiq
from app_huey.admin import enqueue_huey_generate_report as enqueue_huey
from app_q2.admin import enqueue_q2_generate_report as enqueue_q2
from app_tasks_db.admin import enqueue_tasks_db_generate_report as enqueue_tasks_db
from core.models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "source",
        "status",
        "duration_seconds",
        "started_at",
        "finished_at",
        "created_at",
    )
    list_filter = ("source", "status")
    search_fields = ("id",)
    # pyrefly: ignore [bad-override-mutable-attribute]
    actions = (enqueue_huey, enqueue_dramatiq, enqueue_q2, enqueue_tasks_db)
