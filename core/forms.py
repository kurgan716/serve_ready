from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import UserProfile, Lesson, Task, Theme, Question, Answer
from django.core.exceptions import ValidationError
import re

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
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 15,
            'class': 'html-editor',
            'placeholder': 'Введите содержание урока...\nМожно использовать HTML теги:\n<h2>Заголовок</h2>\n<p>Абзац текста</p>\n<ul><li>Элемент списка</li></ul>\n<img src="URL_изображения" alt="Описание">'
        }),
        help_text="Используйте HTML для форматирования. Доступные теги: h1-h6, p, ul, ol, li, strong, em, a, img, table, blockquote"
    )

    video_url = forms.URLField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'https://www.youtube.com/watch?v=... или https://rutube.ru/video/...'
        }),
        help_text="Вставьте ссылку на YouTube или Rutube видео"
    )

    class Meta:
        model = Lesson
        fields = ['title', 'content', 'video_url', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }

    def clean_content(self):
        """Валидация HTML контента"""
        content = self.cleaned_data['content']

        # Список разрешенных HTML тегов
        allowed_tags = {
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'p', 'br', 'hr',
            'strong', 'b', 'em', 'i', 'u', 's',
            'ul', 'ol', 'li',
            'a', 'img',
            'table', 'thead', 'tbody', 'tr', 'th', 'td',
            'blockquote', 'code', 'pre',
            'div', 'span'
        }

        # Проверка на опасные теги
        dangerous_patterns = [
            r'<script.*?>.*?</script>',
            r'<iframe.*?>.*?</iframe>',
            r'<object.*?>.*?</object>',
            r'<embed.*?>',
            r'on\w+=".*?"',
            r'javascript:'
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, content, re.IGNORECASE | re.DOTALL):
                raise ValidationError("Обнаружен небезопасный код в содержании")

        return content

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'file']

class ThemeForm(forms.ModelForm):
    class Meta:
        model = Theme
        fields = ['title', 'description', 'image', 'order']


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'explanation', 'order']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3}),
            'explanation': forms.Textarea(attrs={'rows': 2}),
        }


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text', 'is_correct', 'order']
        widgets = {
            'text': forms.TextInput(attrs={'placeholder': 'Текст ответа'}),
        }


AnswerFormSet = forms.inlineformset_factory(
    Question,
    Answer,
    form=AnswerForm,
    extra=4,  # 4 пустых поля для ответов
    can_delete=True,
    min_num=2,  # минимум 2 ответа
    validate_min=True,
)


class InteractiveTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'task_type', 'max_score']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'task_type': forms.Select(attrs={'class': 'task-type-select'}),
        }


class QuizForm(forms.Form):
    """Форма для прохождения теста"""

    def __init__(self, *args, **kwargs):
        questions = kwargs.pop('questions', [])
        super().__init__(*args, **kwargs)

        for question in questions:
            field_name = f'question_{question.id}'

            if question.task.task_type == 'choice':
                # Один правильный ответ
                choices = [(answer.id, answer.text) for answer in question.answers.all()]
                self.fields[field_name] = forms.ChoiceField(
                    label=question.text,
                    choices=choices,
                    widget=forms.RadioSelect,
                    required=True
                )
            elif question.task.task_type == 'multiple':
                # Несколько правильных ответов
                choices = [(answer.id, answer.text) for answer in question.answers.all()]
                self.fields[field_name] = forms.MultipleChoiceField(
                    label=question.text,
                    choices=choices,
                    widget=forms.CheckboxSelectMultiple,
                    required=True
                )