from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('research/', views.research_view, name='research'),
    path('themes/', views.themes_view, name='themes'),
    path('theme/<int:pk>/', views.theme_detail_view, name='theme_detail'),
    path('lesson/<int:lesson_id>/', views.lesson_detail_view, name='lesson_detail'),
    path('lesson/<int:lesson_id>/complete/', views.mark_lesson_completed, name='mark_lesson_completed'),
    path('theme/<int:theme_id>/add_lesson/', views.add_lesson_view, name='add_lesson'),
    path('lesson/<int:lesson_id>/add_task/', views.add_task_view, name='add_task'),
    path('research/', views.research_view, name='research'),
    path('research/youth/', views.research_youth_view, name='research_youth'),
    path('research/guide/', views.research_guide_view, name='research_guide'),
]