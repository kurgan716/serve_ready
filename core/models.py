from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

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
    content = models.TextField(verbose_name="Содержание урока")
    video_url = models.URLField(blank=True, null=True, verbose_name="Ссылка на видео")
    created_at = models.DateTimeField(auto_now_add=True)
    order = models.IntegerField(default=0, verbose_name="Порядок")
    
    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return self.title

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