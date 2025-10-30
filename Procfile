# Procfile para Render (v2.2.0)
# O Render usa render.yaml por padrão, mas este arquivo serve como fallback

web: gunicorn ifc_monitoring.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --timeout 120 --log-file -
worker: celery -A ifc_monitoring worker --loglevel=info
beat: celery -A ifc_monitoring beat --loglevel=info