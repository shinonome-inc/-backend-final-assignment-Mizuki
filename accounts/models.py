from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import UniqueConstraint


class User(AbstractUser):
    email = models.EmailField()


class FriendShip(models.Model):
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="follower", on_delete=models.CASCADE)
    followee = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="followee", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [UniqueConstraint(fields=["follower", "followee"], name="unique_friendship")]
