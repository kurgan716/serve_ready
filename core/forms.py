from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import UserProfile, Lesson, Task, Theme

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")
    first_name = forms.CharField(max_length=30, required=True, label="Имя")
    last_name = forms.CharField(max_length=30, required=True, label="Фамилия")
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Имя пользователя")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['birth_date', 'phone', 'avatar', 'achievements']

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'content', 'video_url', 'order']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10}),
        }

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'file']

class ThemeForm(forms.ModelForm):
    class Meta:
        model = Theme
        fields = ['title', 'description', 'image', 'order']