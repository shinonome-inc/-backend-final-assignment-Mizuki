from django.contrib import admin

from .models import Like, Tweet

admin.site.register(Tweet)
admin.site.register(Like)
