from django.urls import path

from . import views

app_name = "tweets"

urlpatterns = [
    path("home/", views.HomeView.as_view(), name="home"),
    path("create/", views.TweetCreateView.as_view(), name="create"),
    path("<int:pk>/", views.TweetDetailView.as_view(), name="detail"),
    path("<int:pk>/delete/", views.TweetDeleteView.as_view(), name="delete"),
    path("<int:pk>/like/", views.LikeView.as_view(), name="like"),
    path("<int:pk>/unlike/", views.UnlikeView.as_view(), name="unlike"),
]
