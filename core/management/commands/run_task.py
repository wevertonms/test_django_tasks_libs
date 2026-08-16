from django.core.management.base import BaseCommand

LIBS = ("huey", "dramatiq", "q2", "tasks_db", "chancy", "procrastinate", "taskito")


class Command(BaseCommand):
    help = "Enqueue generate_report(n) on a given library."

    def add_arguments(self, parser):
        parser.add_argument("lib", choices=LIBS)
        parser.add_argument("n", type=int)

    def handle(self, *args, **options):
        lib = options["lib"]
        n = options["n"]

        if lib == "huey":
            from app_huey.tasks import generate_report

            result = generate_report(n)
        elif lib == "dramatiq":
            from app_dramatiq.tasks import generate_report

            result = generate_report.send(n)
        elif lib == "q2":
            from django_q.tasks import async_task

            result = async_task("app_q2.tasks.generate_report", n)
        elif lib == "chancy":
            from app_chancy.tasks import generate_report
            from chancy_instance import chancy

            ref = chancy.sync_push(generate_report.job.with_kwargs(n=n))
            result = str(ref.identifier)
        elif lib == "procrastinate":
            from app_procrastinate.tasks import generate_report

            result = generate_report.defer(n=n)
        elif lib == "taskito":
            from app_taskito.tasks import generate_report

            job = generate_report.delay(n)
            result = job.id
        else:
            from app_tasks_db.tasks import generate_report

            result = generate_report.enqueue(n)

        self.stdout.write(
            self.style.SUCCESS(f"Enqueued generate_report({n}) via {lib} -> {result}")
        )
