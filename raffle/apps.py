from django.apps import AppConfig


class RaffleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'raffle'

def ready(self):
    import raffle.signals  