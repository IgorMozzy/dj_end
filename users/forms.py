from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django import forms
from django.contrib.auth.models import Group
from django.forms import ModelForm

from users.models import CustomUser


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control',
                                                             'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                 'placeholder': 'Password'}))


class GroupForm(ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'permissions']


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), required=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone', 'password']
        exclude = ['password']


class UserRegistrationForm(UserCreationForm):

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'phone', 'password1', 'password2']
