"""
Configuração do Celery para processamento assíncrono de tarefas.
"""

import os
from celery import Celery

# Define o settings module do Django para o Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ifc_monitoring.settings')

app = Celery('ifc_monitoring')

# Carrega configurações do Django settings.py
# usando o namespace 'CELERY' para todas as configurações relacionadas ao Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# Carrega tasks de todos os apps registrados no Django
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    """Task de debug para testar o Celery."""
    print(f'Request: {self.request!r}')

