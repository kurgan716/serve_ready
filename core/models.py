from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe

class Theme(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название темы")
    description = models.TextField(verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True)
    order = models.IntegerField(default=0, verbose_name="Порядок")
    image = models.ImageField(upload_to='themes/', blank=True, null=True, verbose_name="Изображение")
    
    class Meta:
        verbose_name = "Тема"
        verbose_name_plural = "Темы"
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('theme_detail', kwargs={'pk': self.pk})


class Lesson(models.Model):
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, related_name='lessons', verbose_name="Тема")
    title = models.CharField(max_length=200, verbose_name="Название урока")
    content = models.TextField(verbose_name="Содержание урока", help_text="Используйте HTML для форматирования")
    video_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="Ссылка на видео",
        help_text="Ссылка на YouTube или Rutube видео"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    order = models.IntegerField(default=0, verbose_name="Порядок")

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
        ordering = ['order', 'created_at']

    def __str__(self):
        return self.title

    def get_video_embed_code(self):
        """Генерирует embed код для YouTube или Rutube"""
        if not self.video_url:
            return None

        if 'youtube.com' in self.video_url or 'youtu.be' in self.video_url:
            # Извлекаем ID видео для YouTube
            video_id = None
            if 'youtube.com/watch?v=' in self.video_url:
                video_id = self.video_url.split('v=')[1].split('&')[0]
            elif 'youtu.be/' in self.video_url:
                video_id = self.video_url.split('youtu.be/')[1].split('?')[0]

            if video_id:
                return format_html(
                    '<div class="video-container"><iframe src="https://www.youtube.com/embed/{}" '
                    'frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" '
                    'allowfullscreen></iframe></div>',
                    video_id
                )

        elif 'rutube.ru' in self.video_url:
            # Извлекаем ID видео для Rutube
            if 'rutube.ru/video/' in self.video_url:
                video_id = self.video_url.split('rutube.ru/video/')[1].split('/')[0]
                return format_html(
                    '<div class="video-container"><iframe src="https://rutube.ru/play/embed/{}" '
                    'frameborder="0" allow="clipboard-write; autoplay" '
                    'webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe></div>',
                    video_id
                )

        return None

    def safe_content(self):
        """Возвращает безопасный HTML контент"""
        return mark_safe(self.content)


class Task(models.Model):
    TASK_TYPES = [
        ('text', 'Текстовое задание'),
        ('choice', 'Тест с выбором ответа'),
        ('multiple', 'Тест с несколькими правильными ответами'),
        ('file', 'Задание с файлом'),
    ]

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='tasks', verbose_name="Урок")
    title = models.CharField(max_length=200, verbose_name="Название задания")
    description = models.TextField(verbose_name="Описание задания")
    task_type = models.CharField(
        max_length=20,
        choices=TASK_TYPES,
        default='text',
        verbose_name="Тип задания"
    )
    max_score = models.IntegerField(
        default=10,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        verbose_name="Максимальный балл"
    )
    file = models.FileField(upload_to='tasks/', blank=True, null=True, verbose_name="Файл задания")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Задание"
        verbose_name_plural = "Задания"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('lesson_detail', kwargs={'lesson_id': self.lesson.id})


class Question(models.Model):
    """Вопрос для теста"""
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name="Задание"
    )
    text = models.TextField(verbose_name="Текст вопроса")
    order = models.IntegerField(default=0, verbose_name="Порядок")
    explanation = models.TextField(
        blank=True,
        null=True,
        verbose_name="Объяснение ответа"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"Вопрос: {self.text[:50]}..."


class Answer(models.Model):
    """Вариант ответа на вопрос"""
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name="Вопрос"
    )
    text = models.CharField(max_length=500, verbose_name="Текст ответа")
    is_correct = models.BooleanField(default=False, verbose_name="Правильный ответ")
    order = models.IntegerField(default=0, verbose_name="Порядок")

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"
        ordering = ['order']

    def __str__(self):
        return f"{self.text[:50]}... ({'✓' if self.is_correct else '✗'})"


class UserAnswer(models.Model):
    """Ответ пользователя на вопрос"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь"
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        verbose_name="Вопрос"
    )
    selected_answers = models.ManyToManyField(
        Answer,
        verbose_name="Выбранные ответы"
    )
    is_correct = models.BooleanField(default=False, verbose_name="Правильно")
    score = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Баллы"
    )
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Ответ пользователя"
        verbose_name_plural = "Ответы пользователей"
        unique_together = ['user', 'question']

    def __str__(self):
        return f"{self.user.username} - {self.question.text[:30]}..."


class TaskAttempt(models.Model):
    """Попытка выполнения задания пользователем"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь"
    )
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        verbose_name="Задание"
    )
    score = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Баллы"
    )
    max_score = models.IntegerField(
        default=10,
        verbose_name="Максимальный балл"
    )
    percentage = models.FloatField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Процент выполнения"
    )
    is_completed = models.BooleanField(default=False, verbose_name="Завершено")
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Попытка выполнения задания"
        verbose_name_plural = "Попытки выполнения заданий"

    def __str__(self):
        return f"{self.user.username} - {self.task.title} ({self.percentage}%)"

    def calculate_score(self):
        """Рассчитать итоговый балл"""
        user_answers = UserAnswer.objects.filter(
            user=self.user,
            question__task=self.task
        )

        if user_answers.exists():
            correct_answers = user_answers.filter(is_correct=True).count()
            total_questions = self.task.questions.count()

            if total_questions > 0:
                self.percentage = (correct_answers / total_questions) * 100
                self.score = int((self.percentage / 100) * self.max_score)
                self.is_completed = True
                self.completed_at = timezone.now()
                self.save()

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    birth_date = models.DateField(blank=True, null=True, verbose_name="Дата рождения")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name="Аватар")
    completed_lessons = models.ManyToManyField(Lesson, blank=True, verbose_name="Пройденные уроки")
    achievements = models.TextField(blank=True, verbose_name="Достижения")
    
    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"
    
    def __str__(self):
        return self.user.username

class ResearchArticle(models.Model):
    title = models.CharField(max_length=300, verbose_name="Заголовок исследования")
    content = models.TextField(verbose_name="Содержание")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True, verbose_name="Опубликовано")
    
    class Meta:
        verbose_name = "Исследование"
        verbose_name_plural = "Исследования"
    
    def __str__(self):
        return self.title