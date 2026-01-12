from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Theme, Lesson, Task, UserProfile, ResearchArticle

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False

class CustomUserAdmin(UserAdmin):
    inlines = [UserProfileInline]

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ['title', 'order', 'created_at']
    search_fields = ['title', 'description']
    list_filter = ['created_at']

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'theme', 'order', 'created_at']
    search_fields = ['title', 'content']
    list_filter = ['theme', 'created_at']

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'lesson', 'created_at']
    search_fields = ['title', 'description']

@admin.register(ResearchArticle)
class ResearchArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at', 'is_published']
    search_fields = ['title', 'content']
    list_filter = ['is_published', 'created_at']