from django.shortcuts import render, redirect
from .forms import UserLogInForm
from django.views import View
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
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
                if self.next:
                    return redirect(self.next)
                return redirect("home:home")
            messages.error(request, "username or password is wrong", "warning")
        return render(request, self.template_name, {"form": form})


class HomeView(View):
    def get(self, request):
        return render(request, "home/home.html")


class ShowAnswerFlashcard(View):
    def get(self, request):
        pass
