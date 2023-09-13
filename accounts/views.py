from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, View

from tweets.models import Tweet

from .forms import SignupForm
from .models import FriendShip, User


class SignupView(CreateView):
    form_class = SignupForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy(settings.LOGIN_REDIRECT_URL)

    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password1"]
        user = authenticate(self.request, username=username, password=password)
        login(self.request, user)
        return response


class UserProfileView(LoginRequiredMixin, DetailView):
    model = User
    context_object_name = "profile"
    template_name = "accounts/profile.html"
    slug_field = "username"
    slug_url_kwarg = "username"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User, username=self.kwargs["username"])

        context["user"] = user
        context["profile_list"] = Tweet.objects.filter(user=self.object).select_related("user")
        context["following_count"] = FriendShip.objects.filter(follower=self.object).count()
        context["follower_count"] = FriendShip.objects.filter(following=self.object).count()
        context["is_following"] = FriendShip.objects.filter(following=user, follower=self.request.user).exists()

        return context


class FollowView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        follower = self.request.user
        following = get_object_or_404(User, username=self.kwargs["username"])

        if follower == following:
            return HttpResponseBadRequest("自分自身への操作は無効です")
        elif FriendShip.objects.filter(follower=follower, following=following).exists():
            return HttpResponseBadRequest("既にフォロー済みです")
        else:
            FriendShip.objects.create(follower=follower, following=following)
            messages.success(request, f"{following.username}をフォローしました")

        return redirect("tweets:home")


class UnFollowView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        follower = self.request.user
        following = get_object_or_404(User, username=self.kwargs["username"])
        friendship = FriendShip.objects.filter(follower=follower, following=following).first()

        if follower == following:
            return HttpResponseBadRequest("自分自身に対する操作は無効です")
        elif friendship:
            friendship.delete()
            messages.success(request, f"{following.username}をフォロー解除しました")
            return redirect("tweets:home")
        else:
            return HttpResponseBadRequest("フォローしていないユーザーです")


class FollowingListView(LoginRequiredMixin, ListView):
    model = User
    template_name = "accounts/following_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        following = get_object_or_404(User, username=self.kwargs["username"])

        context["following_list"] = FriendShip.objects.filter(follower=following).select_related("following")
        return context


class FollowerListView(LoginRequiredMixin, ListView):
    model = User
    template_name = "accounts/follower_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        follower = get_object_or_404(User, username=self.kwargs["username"])

        context["follower_list"] = FriendShip.objects.filter(following=follower).select_related("follower")
        return context
