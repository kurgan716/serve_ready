from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.db import transaction
from django.utils import timezone
from django.forms import formset_factory
from .models import Theme, Lesson, Task, UserProfile, ResearchArticle, Question, Answer, UserAnswer, TaskAttempt
from .forms import (
    RegisterForm, LoginForm, ProfileUpdateForm, LessonForm,
    TaskForm, ThemeForm, QuestionForm, AnswerFormSet,
    InteractiveTaskForm, QuizForm
)

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
    """Главная страница исследований"""
    # Здесь можно показывать список исследований
    return render(request, 'core/research/index.html')

def research_youth_view(request):
    """Первое исследование о молодёжи"""
    return render(request, 'core/research/research.html')

def research_guide_view(request):
    """Второе исследование - руководство по службе"""
    return render(request, 'core/research/research_guide.html')

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


@login_required
def add_interactive_task(request, lesson_id):
    """Добавить интерактивное задание"""
    if not request.user.is_staff:
        return HttpResponseForbidden("Только администраторы могут добавлять задания")

    lesson = get_object_or_404(Lesson, id=lesson_id)

    if request.method == 'POST':
        task_form = InteractiveTaskForm(request.POST, request.FILES)

        if task_form.is_valid():
            task = task_form.save(commit=False)
            task.lesson = lesson
            task.save()

            # Перенаправляем на создание вопросов
            messages.success(request, 'Задание создано! Теперь добавьте вопросы.')
            return redirect('add_questions', task_id=task.id)
    else:
        task_form = InteractiveTaskForm()

    return render(request, 'core/add_interactive_task.html', {
        'task_form': task_form,
        'lesson': lesson,
    })


@login_required
def add_questions(request, task_id):
    """Добавить вопросы к заданию"""
    if not request.user.is_staff:
        return HttpResponseForbidden("Только администраторы могут добавлять вопросы")

    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        question_form = QuestionForm(request.POST)
        answer_formset = AnswerFormSet(request.POST, instance=None)

        if question_form.is_valid() and answer_formset.is_valid():
            with transaction.atomic():
                # Сохраняем вопрос
                question = question_form.save(commit=False)
                question.task = task
                question.save()

                # Сохраняем ответы
                answer_formset.instance = question
                answer_formset.save()

                # Проверяем, что есть хотя бы один правильный ответ
                correct_answers = question.answers.filter(is_correct=True).count()
                if correct_answers == 0:
                    messages.warning(request, 'Добавьте хотя бы один правильный ответ!')

                # Очищаем форму для следующего вопроса
                if 'add_another' in request.POST:
                    messages.success(request, 'Вопрос добавлен! Добавьте следующий.')
                    return redirect('add_questions', task_id=task.id)
                else:
                    messages.success(request, 'Все вопросы добавлены!')
                    return redirect('lesson_detail', lesson_id=task.lesson.id)
    else:
        question_form = QuestionForm()
        answer_formset = AnswerFormSet(instance=None)

    return render(request, 'core/add_questions.html', {
        'question_form': question_form,
        'answer_formset': answer_formset,
        'task': task,
    })


@login_required
def edit_question(request, question_id):
    """Редактировать вопрос"""
    if not request.user.is_staff:
        return HttpResponseForbidden("Только администраторы могут редактировать вопросы")

    question = get_object_or_404(Question, id=question_id)
    task = question.task

    if request.method == 'POST':
        question_form = QuestionForm(request.POST, instance=question)
        answer_formset = AnswerFormSet(request.POST, instance=question)

        if question_form.is_valid() and answer_formset.is_valid():
            with transaction.atomic():
                question_form.save()
                answer_formset.save()
                messages.success(request, 'Вопрос обновлен!')
                return redirect('manage_questions', task_id=task.id)
    else:
        question_form = QuestionForm(instance=question)
        answer_formset = AnswerFormSet(instance=question)

    return render(request, 'core/edit_question.html', {
        'question_form': question_form,
        'answer_formset': answer_formset,
        'question': question,
        'task': task,
    })


@login_required
def manage_questions(request, task_id):
    """Управление вопросами задания"""
    if not request.user.is_staff:
        return HttpResponseForbidden("Только администраторы могут управлять вопросами")

    task = get_object_or_404(Task, id=task_id)
    questions = task.questions.all().order_by('order')

    return render(request, 'core/manage_questions.html', {
        'task': task,
        'questions': questions,
    })


@login_required
def take_quiz(request, task_id):
    """Пройти тест"""
    task = get_object_or_404(Task, id=task_id)
    questions = task.questions.all().order_by('order')

    if questions.count() == 0:
        messages.warning(request, 'В этом задании еще нет вопросов.')
        return redirect('lesson_detail', lesson_id=task.lesson.id)

    # Создаем или получаем попытку
    attempt, created = TaskAttempt.objects.get_or_create(
        user=request.user,
        task=task,
        defaults={'max_score': task.max_score}
    )

    if attempt.is_completed:
        messages.info(request, 'Вы уже прошли этот тест. Результаты ниже.')
        return redirect('quiz_results', attempt_id=attempt.id)

    if request.method == 'POST':
        form = QuizForm(request.POST, questions=questions)

        if form.is_valid():
            with transaction.atomic():
                total_correct = 0

                # Сохраняем ответы пользователя
                for question in questions:
                    field_name = f'question_{question.id}'
                    selected_ids = form.cleaned_data.get(field_name, [])

                    if not isinstance(selected_ids, list):
                        selected_ids = [selected_ids]

                    selected_answers = Answer.objects.filter(id__in=selected_ids)

                    # Создаем запись ответа пользователя
                    user_answer, created = UserAnswer.objects.get_or_create(
                        user=request.user,
                        question=question
                    )

                    # Очищаем старые ответы
                    user_answer.selected_answers.clear()

                    # Добавляем выбранные ответы
                    for answer in selected_answers:
                        user_answer.selected_answers.add(answer)

                    # Проверяем правильность
                    if task.task_type == 'choice':
                        # Для одного правильного ответа
                        correct_answer = question.answers.filter(is_correct=True).first()
                        user_answer.is_correct = (
                                correct_answer and
                                correct_answer.id in selected_ids
                        )
                    elif task.task_type == 'multiple':
                        # Для нескольких правильных ответов
                        correct_answers = set(question.answers.filter(is_correct=True).values_list('id', flat=True))
                        selected_ids_set = set(map(int, selected_ids))
                        user_answer.is_correct = (correct_answers == selected_ids_set)

                    user_answer.score = task.max_score if user_answer.is_correct else 0
                    user_answer.save()

                    if user_answer.is_correct:
                        total_correct += 1

                # Обновляем попытку
                attempt.calculate_score()
                messages.success(request, f'Тест завершен! Ваш результат: {attempt.percentage:.1f}%')

                return redirect('quiz_results', attempt_id=attempt.id)
    else:
        form = QuizForm(questions=questions)

    return render(request, 'core/take_quiz.html', {
        'task': task,
        'questions': questions,
        'form': form,
        'attempt': attempt,
    })


@login_required
def quiz_results(request, attempt_id):
    """Результаты теста"""
    attempt = get_object_or_404(TaskAttempt, id=attempt_id, user=request.user)
    user_answers = UserAnswer.objects.filter(
        user=request.user,
        question__task=attempt.task
    ).select_related('question')

    return render(request, 'core/quiz_results.html', {
        'attempt': attempt,
        'user_answers': user_answers,
        'task': attempt.task,
    })


@login_required
def retake_quiz(request, task_id):
    """Перепройти тест"""
    task = get_object_or_404(Task, id=task_id)

    # Удаляем старые ответы
    UserAnswer.objects.filter(
        user=request.user,
        question__task=task
    ).delete()

    # Удаляем старую попытку
    TaskAttempt.objects.filter(
        user=request.user,
        task=task
    ).delete()

    messages.info(request, 'Тест сброшен. Можете начать заново.')
    return redirect('take_quiz', task_id=task.id)