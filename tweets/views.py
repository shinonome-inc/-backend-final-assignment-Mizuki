# from django.shortcuts import render
from typing import Any
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, DeleteView, DetailView, ListView, View
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from .models import Tweet, Like


class HomeView(LoginRequiredMixin, ListView):
    model = Tweet
    template_name = "tweets/home.html"
    context_object_name = "tweet_list"
    queryset = Tweet.objects.select_related("user")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["liked_list"] = Like.objects.filter(user=self.request.user)
        return context


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
    context_object_name = "tweet_detail"
    template_name = "tweets/detail.html"


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
        is_liked = False

        Like.objects.get_or_create(user=user, tweet=tweet)
        likes_count = Like.objects.count()
        context = {
            "likes_count": likes_count,
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
        is_liked = True

        like = Like.objects.filter(user=user, tweet=tweet)
        like.delete()
        likes_count = Like.objects.count()
        context = {
            "likes_count": likes_count,
            "is_liked": is_liked,
            "tweet_id": tweet_id,
            "like_url": like_url,
        }

        return JsonResponse(context)
