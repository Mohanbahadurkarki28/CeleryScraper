import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hosting_project.settings')

app = Celery('hosting_project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# --- Add periodic task schedule here ---
app.conf.beat_schedule = {
    'scrape-all-hosting-plans': {
        'task': 'plans.tasks.scrape_hosting_plans_task', 
        'schedule': crontab(minute=0, hour='*'),
    },
}

app.conf.timezone = 'Asia/Kathmandu'
