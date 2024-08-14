from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserLogInForm, UserRegisterForm
from django.views import View
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView
from .forms import FlashCardForm, ReviewForm, AnswerForm
from api.models import FlashCard, UserFlashCard
from fsrs import FSRS, Card, ReviewLog, Rating
from datetime import datetime, timezone


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
    form_class = ReviewForm
    template_true = 'home/review_flashcard.html'
    template_false = 'home/flashcard_result.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.flashcard = get_object_or_404(FlashCard, pk=kwargs["pk"])
        self.is_correct = (self.flashcard.real_answer == kwargs["selected_answer"])
        self.user_flashcard, created = UserFlashCard.objects.get_or_create(
            user=request.user,
            flashcard=self.flashcard,
            defaults={'card_data': Card().to_dict()}
        )
        
        # Check if the review time is invalid and redirect if so
        if self.process_invalid_answer():
            messages.warning(request, "This flashcard is not yet due for review.")
            return redirect('home:flashcard_list')
        
        return super().dispatch(request, *args, **kwargs)
    
    def process_incorrect_answer(self, f, card):
        rate = Rating(Rating.Again)
        self.update_user_flashcard(f, card, rate)
        return render(self.request, self.template_false, {'flashcard': self.flashcard, 'is_correct': self.is_correct})

    def process_invalid_answer(self):
        return bool(
            Card.from_dict(self.user_flashcard.card_data).due
            >= datetime.now(timezone.utc)
            and self.user_flashcard.review_log
        )

    def update_user_flashcard(self, f, card, rate):
        review_log = (
            ReviewLog.from_dict(self.user_flashcard.review_log)
            if self.user_flashcard.review_log
            else None
        )
        card, review_log = f.review_card(card, rate)
        self.user_flashcard.card_data = card.to_dict()
        self.user_flashcard.review_log = review_log.to_dict()
        self.user_flashcard.save()

    def get(self, request, *args, **kwargs):
        f = FSRS()
        card = Card.from_dict(self.user_flashcard.card_data)
        
        if self.is_correct:
            return render(request, self.template_true, {'flashcard': self.flashcard, 'form': self.form_class(), 'is_correct': self.is_correct})
        else:
            return self.process_incorrect_answer(f, card)
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        
        if form.is_valid():
            rating = int(form.cleaned_data['rating'])
            f = FSRS()
            card = Card.from_dict(self.user_flashcard.card_data)
            rate = Rating(rating)
            
            self.update_user_flashcard(f, card, rate)
            messages.success(request, "Your review was successfully saved.")
            return redirect('home:flashcard_list')
        
        # If form is not valid, render the template again with errors
        return render(request, self.template_true, {'flashcard': self.flashcard, 'form': form})
