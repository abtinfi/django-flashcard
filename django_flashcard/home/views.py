from django.shortcuts import render
from django.views import View
# Create your views here.
from django.http import HttpResponse


class HomeView(View):
    def get(self, request):
        return render(request, "home/home.html")