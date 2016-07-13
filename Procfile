web: gunicorn connect.wsgi --log-file -
worker: python manage.py celeryd
worker: python manage.py celerybeat