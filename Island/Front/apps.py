from django.apps import AppConfig


class FrontConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Front'

    def ready(self):
        from .scheduler import start
        start()