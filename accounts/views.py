from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView

from .forms import LoginForm, SignupForm


class SignupView(CreateView):
    form_class = SignupForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy("tweets:home")

    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password1"]
        user = authenticate(self.request, username=username, password=password)
        login(self.request, user)
        return response


class LoginVIew(LoginView):
    form_class = LoginForm
    template_name = "registration/login.html"


class LogoutView(LogoutView):
    pass


class UserProfileView(LoginRequiredMixin, View):
    login_url = "../../accounts/login"

    def get(self, request, *args, **kwargs):
        return render(request, "accounts/profile.html")
