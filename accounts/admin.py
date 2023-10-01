from django.contrib import admin

from .models import FriendShip, User

admin.site.register(User)
admin.site.register(FriendShip)
