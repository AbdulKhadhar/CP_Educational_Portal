# quizzes/admin.py
from django.contrib import admin
from .models import Quiz, QuizQuestion, QuizOption, QuizAttempt, QuizAnswer, QuizResult

class QuizOptionInline(admin.TabularInline):
    model = QuizOption
    extra = 4

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'section', 'difficulty', 'start_time', 'end_time', 'is_active']
    list_filter = ['difficulty', 'is_active', 'start_time']
    search_fields = ['title', 'section__course__name']
    raw_id_fields = ['section', 'created_by']

@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ['quiz', 'question_type', 'marks', 'order']
    list_filter = ['question_type', 'quiz']
    search_fields = ['question_text', 'quiz__title']
    inlines = [QuizOptionInline]
    raw_id_fields = ['quiz']

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['quiz', 'student', 'attempt_number', 'status', 'score', 'percentage', 'started_at']
    list_filter = ['status', 'started_at', 'quiz']
    search_fields = ['student__roll_number', 'quiz__title']
    raw_id_fields = ['quiz', 'student']

@admin.register(QuizAnswer)
class QuizAnswerAdmin(admin.ModelAdmin):
    list_display = ['attempt', 'question', 'is_correct', 'marks_awarded']
    list_filter = ['is_correct', 'answered_at']
    search_fields = ['attempt__student__roll_number', 'question__question_text']
    raw_id_fields = ['attempt', 'question']

@admin.register(QuizResult)
class QuizResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'quiz', 'score', 'percentage', 'passed', 'rank', 'completed_at']
    list_filter = ['passed', 'completed_at', 'quiz']
    search_fields = ['student__roll_number', 'quiz__title']
    raw_id_fields = ['attempt', 'student', 'quiz']
