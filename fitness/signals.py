from .models import Referral,User
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save,sender=User)
def postSaveCreateProfile(sender,instance,created, *args, **kwargs):
    if created:
        Referral.objects.create(user=instance)