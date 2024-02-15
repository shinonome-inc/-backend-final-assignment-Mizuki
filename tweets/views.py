# from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Prefetch
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, View

from .models import Like, Tweet

# ListViewはquerysetで取得する
# queryset使わずcontextで渡すならTemplateViewでいい


class HomeView(LoginRequiredMixin, ListView):
    model = Tweet
    template_name = "tweets/home.html"
    context_object_name = "tweet_list"

    def get_queryset(self):
        user = self.request.user
        queryset = (
            Tweet.objects.select_related("user")
            .prefetch_related(Prefetch("likes", queryset=Like.objects.filter(user=user), to_attr="is_liked"))
            .annotate(liked_count=Count("likes"))
        )
        return queryset


class TweetCreateView(LoginRequiredMixin, CreateView):
    model = Tweet
    fields = ["content"]
    template_name = "tweets/tweet.html"
    success_url = reverse_lazy("tweets:home")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class TweetDetailView(LoginRequiredMixin, DetailView):
    model = Tweet
    context_object_name = "tweet"
    template_name = "tweets/detail.html"

    def get_queryset(self):
        user = self.request.user
        queryset = (
            Tweet.objects.select_related("user")
            .prefetch_related(Prefetch("likes", queryset=Like.objects.filter(user=user), to_attr="is_liked"))
            .annotate(liked_count=Count("likes"))
        )
        return queryset


class TweetDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Tweet
    context_object_name = "tweet_delete"
    template_name = "tweets/delete.html"
    success_url = reverse_lazy("tweets:home")

    def test_func(self):
        tweet = self.get_object()
        return tweet.user == self.request.user


class LikeView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        user = self.request.user
        tweet_id = self.kwargs["pk"]
        tweet = get_object_or_404(Tweet, id=tweet_id)
        unlike_url = reverse("tweets:unlike", kwargs={"pk": tweet_id})
        is_liked = True

        Like.objects.get_or_create(user=user, tweet=tweet)
        likes_count = Like.objects.filter(tweet=tweet).count()
        context = {
            "liked_count": likes_count,
            "is_liked": is_liked,
            "tweet_id": tweet_id,
            "unlike_url": unlike_url,
        }

        return JsonResponse(context)


class UnlikeView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        user = self.request.user
        tweet_id = self.kwargs["pk"]
        tweet = get_object_or_404(Tweet, id=tweet_id)
        like_url = reverse("tweets:like", kwargs={"pk": tweet_id})
        is_liked = False

        like = Like.objects.filter(user=user, tweet=tweet)
        like.delete()
        likes_count = Like.objects.filter(tweet=tweet).count()
        context = {
            "liked_count": likes_count,
            "is_liked": is_liked,
            "tweet_id": tweet_id,
            "like_url": like_url,
        }

        return JsonResponse(context)
