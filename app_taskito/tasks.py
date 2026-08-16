import time

from asgiref.sync import sync_to_async
from taskito.contrib.django.settings import get_queue

queue = get_queue()


@queue.task(max_retries=3)
@sync_to_async
def generate_report(n: int):
    from django.utils import timezone

    from core.models import Report

    report = Report.objects.create(
        source=Report.Source.TASKITO,
        status=Report.Status.RUNNING,
        duration_seconds=n,
        started_at=timezone.now(),
    )
    time.sleep(n)
    report.status = Report.Status.FINISHED
    report.finished_at = timezone.now()
    report.save(update_fields=["status", "finished_at"])
    return str(report.pk)
