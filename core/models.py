from django.db import models


class Report(models.Model):
    class Source(models.TextChoices):
        HUEY = "huey", "Huey"
        DRAMATIQ = "dramatiq", "Dramatiq"
        Q2 = "q2", "Django-Q2"
        TASKS_DB = "tasks_db", "Django Tasks (DB)"
        CHANCY = "chancy", "Chancy"
        PROCRASTINATE = "procrastinate", "Procrastinate"
        FLEXIQ = "flexiq", "FlexiQ"

    class Status(models.TextChoices):
        RUNNING = "running", "Running"
        FINISHED = "finished", "Finished"
        FAILED = "failed", "Failed"

    source = models.CharField(max_length=20, choices=Source.choices, db_index=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.RUNNING, db_index=True
    )
    duration_seconds = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.source}:{self.get_status_display()}:{self.pk}"
