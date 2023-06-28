from celery import Celery

app = Celery('wisd_2023_pipeline')
app.config_from_object('celeryconfig')
