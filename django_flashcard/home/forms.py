from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django import forms
from api.models import FlashCard, UserFlashCard

class UserRegisterForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    email = forms.EmailField(
        required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        label="confirm password",
    )

    def clean_email(self):
        email = self.cleaned_data["email"]
        if user := User.objects.filter(email=email).exists():
            raise ValidationError("this email already exists")
        return email

    def clean_username(self):
        username = self.cleaned_data["username"]
        if user:=User.objects.filter(username=username).exists():
            raise ValidationError("this username already exists")
        return username

    def clean(self):
        cd = super().clean()
        p1 = cd.get("password")
        p2 = cd.get("confirm_password")

        if p1 and p2 and p1 != p2:
            raise ValidationError("passwords must mach")


class UserLogInForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}), label="username/email"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )


class FlashCardForm(forms.ModelForm):
    class Meta:
        model = FlashCard
        fields = ['question', 'real_answer', 'possible_answers']

class ReviewForm(forms.Form):
    RATING_CHOICES = [
        (1, 'Again'),
        (2, 'Hard'),
        (3, 'Good'),
        (4, 'Easy'),
    ]
    rating = forms.ChoiceField(choices=RATING_CHOICES, widget=forms.RadioSelect)


class AnswerForm(forms.Form):
    selected_answer = forms.ChoiceField(choices=[], widget=forms.RadioSelect)

    def __init__(self, *args, **kwargs):
        choices = kwargs.pop('choices', [])
        super().__init__(*args, **kwargs)
        self.fields['selected_answer'].choices = choices