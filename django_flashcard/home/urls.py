from django.urls import path
from . import views

app_name = "home"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path(
        "flashcard/<int:card_id>", views.ShowAnswerFlashcard.as_view(), name="show_card"
    ),
    path("login/", views.UserLoginView.as_view(), name="user_login"),
    path("register/", views.UserRegisterView.as_view(), name="user_register"),
    path("logout/", views.UserLogoutViwe.as_view(), name="user_logout")
]
