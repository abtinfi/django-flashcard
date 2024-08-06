from django.shortcuts import render, redirect
from .forms import UserLogInForm, UserRegisterForm
from django.views import View
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.


class UserLoginView(View):
    form_class = UserLogInForm
    template_name = "home/login.html"

    def setup(self, request, *args, **kwargs):
        self.next = request.GET.get("next", None)
        return super().setup(request, *args, **kwargs)

    def get(self, request):
        form = self.form_class
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(
                request, username=cd["username"], password=cd["password"]
            )
            if user is not None:
                login(request, user)
                messages.success(request, "user login successfuly", "success")
                return redirect(self.next) if self.next else redirect("home:home")
            messages.error(request, "username or password is wrong", "warning")
        return render(request, self.template_name, {"form": form})
class UserRegisterView(View):
    form_class = UserRegisterForm
    template_form = "home/register.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home:home")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_form, {"form": form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = User.objects.create_user(
                username=cd["username"], email=cd["email"], password=cd["password"]
            )
            messages.success(request, "you registered successfuly", "success")
            return redirect("home:home")
        return render(request, self.template_form, {"form": form})

class UserLogoutViwe(LoginRequiredMixin,View):
    def get(self, request):
        logout(request)
        messages.success(request, "user logout successfuly", "success")
        return redirect("home:home")

class HomeView(View):
    def get(self, request):
        return render(request, "home/home.html")


class ShowAnswerFlashcard(View):
    def get(self, request):
        pass
