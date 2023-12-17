from django.contrib import admin

from .models import Tweet, Like

admin.site.register(Tweet)
admin.site.register(Like)
