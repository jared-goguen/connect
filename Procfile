web: gunicorn connect.wsgi --log-file -
worker: celery worker --app=connect.celery.app
beat: celery beat