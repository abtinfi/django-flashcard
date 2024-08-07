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
    path("logout/", views.UserLogoutViwe.as_view(), name="user_logout"),
    path("flashcards/add/", views.FlashCardCreateView.as_view(), name="add_flashcard"),
    path(
        "flashcards/<int:pk>/review/",
        views.FlashCardReviewView.as_view(),
        name="review_flashcard",
    ),
    path("flashcards/", views.FlashCardListView.as_view(), name="flashcard_list"),
    path(
        "flashcards/<int:pk>/question/",
        views.FlashCardQuestionView.as_view(),
        name="flashcard_question",
    ),
    path(
        "flashcards/<int:pk>/result/<str:selected_answer>/",
        views.FlashCardResultView.as_view(),
        name="flashcard_result",
    ),
]
