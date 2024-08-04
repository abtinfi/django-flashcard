from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django import forms


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
