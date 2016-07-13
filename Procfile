web: gunicorn connect.wsgi --log-file -
worker: python manage.py celeryd
beat: python manage.py celerybeat