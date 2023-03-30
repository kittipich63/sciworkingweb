web: gunicorn sciworkingweb_3.wsgi:application --log-file -
release: docker-compose run web python manage.py migrate 