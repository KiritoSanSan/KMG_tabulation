from django.apps import AppConfig


class TabelConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tabel'
    verbose_name =  'Табеля'

    def ready(self) :
        from . import signals