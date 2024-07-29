from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
from .tasks import reset_rocket_inventory

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")

    scheduler.add_job(
        reset_rocket_inventory,
        'interval',
        hours=24,
        name='reset_rocket_inventory',
        jobstore='default',
    )

    register_events(scheduler)
    scheduler.start()
    print("Scheduler started...")
