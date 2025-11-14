from django.urls import path
from . import views

urlpatterns = [
    # Quiz management
    path('', views.quiz_list, name='quiz_list'),
    path('create/<int:section_id>/', views.quiz_create, name='quiz_create'),
    path('<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),
    path('<int:quiz_id>/edit/', views.quiz_edit, name='quiz_edit'),
    path('<int:quiz_id>/delete/', views.quiz_delete, name='quiz_delete'),
    
    # Question management
    path('<int:quiz_id>/add-question/', views.add_question, name='add_question'),
    path('question/<int:question_id>/edit/', views.edit_question, name='edit_question'),
    path('question/<int:question_id>/delete/', views.delete_question, name='delete_question'),
    
    # Taking quiz
    path('<int:quiz_id>/take/', views.take_quiz, name='take_quiz'),
    path('attempt/<int:attempt_id>/submit/', views.submit_quiz, name='submit_quiz'),
    path('attempt/<int:attempt_id>/result/', views.quiz_result, name='quiz_result'),
    
    # Results & analytics
    path('<int:quiz_id>/results/', views.quiz_results, name='quiz_results'),
    path('<int:quiz_id>/analytics/', views.quiz_analytics, name='quiz_analytics'),
]