from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
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
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='tasks', verbose_name="Урок")
    title = models.CharField(max_length=200, verbose_name="Название задания")
    description = models.TextField(verbose_name="Описание задания")
    file = models.FileField(upload_to='tasks/', blank=True, null=True, verbose_name="Файл задания")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Задание"
        verbose_name_plural = "Задания"
    
    def __str__(self):
        return self.title

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