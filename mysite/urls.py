from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("tweets/", include("tweets.urls")),
    path("", include("welcome.urls")),
]

if settings.SQL_DEBUG:
    import debug_toolbar

    urlpatterns += [
        path("__debug__", include(debug_toolbar.urls)),
    ]
