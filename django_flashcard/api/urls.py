from . import views
from django.urls import path

urlpatterns = [
    path('register/', views.ApiRegister.as_view(), name="user_register")
]
