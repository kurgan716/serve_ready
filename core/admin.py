from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Theme, Lesson, Task, UserProfile, ResearchArticle, Question, Answer, UserAnswer, TaskAttempt

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

@admin.register(ResearchArticle)
class ResearchArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at', 'is_published']
    search_fields = ['title', 'content']
    list_filter = ['is_published', 'created_at']

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4
    fields = ['text', 'is_correct', 'order']

class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'task', 'order']
    list_filter = ['task', 'task__lesson']
    search_fields = ['text']
    inlines = [AnswerInline]
    ordering = ['task', 'order']

class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'lesson', 'task_type', 'max_score', 'created_at']
    list_filter = ['task_type', 'lesson__theme']
    search_fields = ['title', 'description']

class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ['user', 'question', 'is_correct', 'score', 'submitted_at']
    list_filter = ['is_correct', 'user', 'question__task']
    search_fields = ['user__username', 'question__text']

class TaskAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'task', 'score', 'percentage', 'is_completed', 'completed_at']
    list_filter = ['is_completed', 'user', 'task']
    search_fields = ['user__username', 'task__title']

admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer)
admin.site.register(UserAnswer, UserAnswerAdmin)
admin.site.register(TaskAttempt, TaskAttemptAdmin)
