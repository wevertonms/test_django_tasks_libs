import time

from django.utils import timezone
from django_rq import job

from core.models import Report

SOURCE = Report.Source.RQ


@job
def generate_report(n: int):
    report = Report.objects.create(
        source=SOURCE,
        status=Report.Status.RUNNING,
        duration_seconds=n,
        started_at=timezone.now(),
    )
    time.sleep(n)
    report.status = Report.Status.FINISHED
    report.finished_at = timezone.now()
    report.save(update_fields=["status", "finished_at"])
    return str(report.pk)
