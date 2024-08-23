from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Raffle


@receiver(post_save, sender=Raffle)#Django's signal receivers
@receiver(post_delete, sender=Raffle)
def invalidate_raffle_cache(sender, instance, **kwargs):
    """
    Invalidates the cache for a raffle when it is saved or deleted.

    This ensures that any cached data related to the raffle is cleared 
    and the latest data is fetched from the database.
    """
   
    cache.delete('raffle_list')
