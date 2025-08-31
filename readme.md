#TO run the projects
    python manage.py runserver


#to Run REDIS
     C:\Redis\redis-server.exe


#TO run the celery
  celery -A hosting_project worker -l info -P solo

    Starts a Celery worker process.
    It listens for tasks from Django (via Redis) and executes them in the background.
    -A hosting_project → points to your Django project.
    -l info → sets logging level.
    -P solo → uses solo execution pool (needed on Windows).


 celery -A hosting_project beat -l info
 
    Starts Celery Beat, which is the scheduler.
    It triggers periodic tasks (like cron jobs), e.g., every hour/day updates.
    Beat puts scheduled tasks into Redis → workers pick them up.


#To update manually
    python manage.py update_plans
