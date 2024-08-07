from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserLogInForm, UserRegisterForm
from django.views import View
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView
from .forms import FlashCardForm, ReviewForm, AnswerForm
from api.models import FlashCard, UserFlashCard
from fsrs import FSRS, Card, ReviewLog, Rating
from datetime import datetime, timezone
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

class SuperUserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser

class FlashCardCreateView(LoginRequiredMixin, SuperUserRequiredMixin, CreateView):
    model = FlashCard
    form_class = FlashCardForm
    template_name = 'home/add_flashcard.html'
    success_url = reverse_lazy('home:flashcard_list')


class FlashCardListView(LoginRequiredMixin, ListView):
    model = FlashCard
    template_name = 'home/flashcard_list.html'
    context_object_name = 'flashcards'

    def get_queryset(self):
        user = self.request.user
        due_flashcards = []
        all_flashcards = FlashCard.objects.all()
        user_flashcards = UserFlashCard.objects.filter(user=user)

        # Create a set of flashcards that the user has already reviewed
        reviewed_flashcards_ids = {uf.flashcard.id for uf in user_flashcards}

        # Find due flashcards
        for user_flashcard in user_flashcards:
            card = Card.from_dict(user_flashcard.card_data)
            if card.due <= datetime.now(timezone.utc):
                due_flashcards.append(user_flashcard.flashcard)

        # Find flashcards that the user has not yet reviewed
        new_flashcards = all_flashcards.exclude(id__in=reviewed_flashcards_ids)

        return list(due_flashcards) + list(new_flashcards)
# views.py
class FlashCardReviewView(LoginRequiredMixin, View):
    model = FlashCard
    form_class = ReviewForm
    template_name = 'home/review_flashcard.html'
    context_object_name = 'flashcard'

    def get_object(self):
        return get_object_or_404(FlashCard, pk=self.kwargs['pk'])

    def get(self, request, *args, **kwargs):
        flashcard = self.get_object()
        form = self.form_class()
        return render(request, self.template_name, {'flashcard': flashcard, 'form': form})

    def post(self, request, *args, **kwargs):
        flashcard = self.get_object()
        form = self.form_class(request.POST)
        if form.is_valid():
            rating = int(form.cleaned_data['rating'])
            f = FSRS()
            user_flashcard, created = UserFlashCard.objects.get_or_create(
                user=self.request.user,
                flashcard=flashcard,
                defaults={'card_data': Card().to_dict()}
            )
            card = Card.from_dict(user_flashcard.card_data)
            rate = Rating(rating)
            if user_flashcard.review_log:
                review_log = ReviewLog.from_dict(user_flashcard.review_log)
                card, review_log = f.review_card(card, rate)
            else:
                card, review_log = f.review_card(card, rate)
            user_flashcard.card_data = card.to_dict()
            user_flashcard.review_log = review_log.to_dict()
            user_flashcard.save()
            return redirect('home:flashcard_list')
        return render(request, self.template_name, {'flashcard': flashcard, 'form': form})



class FlashCardQuestionView(LoginRequiredMixin, View):
    def get(self, request, pk):
        flashcard = get_object_or_404(FlashCard, pk=pk)
        form = AnswerForm(choices=[(ans, ans) for ans in flashcard.possible_answers])
        return render(request, 'home/flashcard_question.html', {'flashcard': flashcard, 'form': form})

    def post(self, request, pk):
        flashcard = get_object_or_404(FlashCard, pk=pk)
        form = AnswerForm(request.POST, choices=[(ans, ans) for ans in flashcard.possible_answers])
        if form.is_valid():
            selected_answer = form.cleaned_data['selected_answer']
            return redirect('home:flashcard_result', pk=pk, selected_answer=selected_answer)
        return render(request, 'home/flashcard_question.html', {'flashcard': flashcard, 'form': form})


class FlashCardResultView(LoginRequiredMixin, View):
    def get(self, request, pk, selected_answer):
        flashcard = get_object_or_404(FlashCard, pk=pk)
        is_correct = (selected_answer == flashcard.real_answer)
        # به‌روزرسانی داده‌های فلش کارت با استفاده از FSRS
        user_flashcard, created = UserFlashCard.objects.get_or_create(
            user=request.user,
            flashcard=flashcard,
            defaults={'card_data': Card().to_dict()}
        )
        f = FSRS()
        card = Card.from_dict(user_flashcard.card_data)
        rate = Rating(4 if is_correct else 1)  # مثال: 4 برای درست و 1 برای غلط
        if user_flashcard.review_log:
            review_log = ReviewLog.from_dict(user_flashcard.review_log)
            card, review_log = f.review_card(card, rate)
        else:
            card, review_log = f.review_card(card, rate)
        user_flashcard.card_data = card.to_dict()
        user_flashcard.review_log = review_log.to_dict()
        user_flashcard.save()
        return render(request, 'home/flashcard_result.html', {'flashcard': flashcard, 'is_correct': is_correct})