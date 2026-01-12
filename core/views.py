
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.utils import timezone

from .models import Theme, Lesson, Task, UserProfile, ResearchArticle
from .forms import RegisterForm, LoginForm, ProfileUpdateForm, LessonForm, TaskForm, ThemeForm

def index(request):
    themes = Theme.objects.all()[:4]
    return render(request, 'core/index.html', {'themes': themes})

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            messages.success(request, 'Регистрация прошла успешно! Теперь вы можете войти.')
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'core/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {username}!')
                return redirect('profile')
    else:
        form = LoginForm()
    return render(request, 'core/login.html', {'form': form})


@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=profile)

    completed_count = profile.completed_lessons.count()
    total_lessons = Lesson.objects.count()

    # Разделяем достижения по запятым для шаблона
    achievements_list = []
    if profile.achievements:
        achievements_list = [a.strip() for a in profile.achievements.split(',') if a.strip()]

    # Подсчитываем выполненные задания
    tasks_completed = Task.objects.filter(
        lesson__in=profile.completed_lessons.all()
    ).count()

    # Вычисляем дни активности
    days_active = (timezone.now() - request.user.date_joined).days

    return render(request, 'core/profile.html', {
        'profile': profile,
        'form': form,
        'completed_count': completed_count,
        'total_lessons': total_lessons,
        'achievements_list': achievements_list,
        'tasks_completed': tasks_completed,
        'days_active': max(days_active, 1),
    })

@login_required
def mark_lesson_completed(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    profile = UserProfile.objects.get(user=request.user)
    
    if lesson in profile.completed_lessons.all():
        profile.completed_lessons.remove(lesson)
        messages.info(request, 'Урок помечен как непройденный')
    else:
        profile.completed_lessons.add(lesson)
        messages.success(request, 'Урок помечен как пройденный!')
    
    return redirect('lesson_detail', lesson_id=lesson_id)

def research_view(request):
    articles = ResearchArticle.objects.filter(is_published=True)
    return render(request, 'core/research.html', {'articles': articles})

def themes_view(request):
    themes = Theme.objects.all().order_by('order')
    return render(request, 'core/themes.html', {'themes': themes})

def theme_detail_view(request, pk):
    theme = get_object_or_404(Theme, pk=pk)
    lessons = theme.lessons.all().order_by('order')
    return render(request, 'core/theme_detail.html', {'theme': theme, 'lessons': lessons})

def lesson_detail_view(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    tasks = lesson.tasks.all()
    is_completed = False
    
    if request.user.is_authenticated:
        profile = UserProfile.objects.get(user=request.user)
        is_completed = lesson in profile.completed_lessons.all()
    
    return render(request, 'core/lesson_detail.html', {
        'lesson': lesson,
        'tasks': tasks,
        'is_completed': is_completed,
    })

@login_required
def add_lesson_view(request, theme_id):
    if not request.user.is_staff:
        return HttpResponseForbidden("Только администраторы могут добавлять уроки")
    
    theme = get_object_or_404(Theme, id=theme_id)
    
    if request.method == 'POST':
        form = LessonForm(request.POST)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.theme = theme
            lesson.save()
            messages.success(request, 'Урок успешно добавлен!')
            return redirect('theme_detail', pk=theme.pk)
    else:
        form = LessonForm()
    
    return render(request, 'core/add_lesson.html', {'form': form, 'theme': theme})

@login_required
def add_task_view(request, lesson_id):
    if not request.user.is_staff:
        return HttpResponseForbidden("Только администраторы могут добавлять задания")
    
    lesson = get_object_or_404(Lesson, id=lesson_id)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES)
        if form.is_valid():
            task = form.save(commit=False)
            task.lesson = lesson
            task.save()
            messages.success(request, 'Задание успешно добавлено!')
            return redirect('lesson_detail', lesson_id=lesson.id)
    else:
        form = TaskForm()
    
    return render(request, 'core/add_task.html', {'form': form, 'lesson': lesson})

def logout_view(request):
    logout(request)
    messages.info(request, 'Вы успешно вышли из системы.')
    return redirect('index')