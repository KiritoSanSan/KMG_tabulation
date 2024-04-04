from django.apps import AppConfig


class GraphConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'graph'

    def ready(self):
        from . import signals

