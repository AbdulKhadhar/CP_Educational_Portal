
# quizzes/forms.py
from django import forms
from .models import Quiz, QuizQuestion, QuizOption

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'description', 'duration_minutes', 'total_marks', 'passing_marks',
                 'difficulty', 'start_time', 'end_time', 'allow_multiple_attempts', 
                 'max_attempts', 'show_results_immediately', 'randomize_questions']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_marks': forms.NumberInput(attrs={'class': 'form-control'}),
            'passing_marks': forms.NumberInput(attrs={'class': 'form-control'}),
            'difficulty': forms.Select(attrs={'class': 'form-select'}),
            'start_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'allow_multiple_attempts': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'max_attempts': forms.NumberInput(attrs={'class': 'form-control'}),
            'show_results_immediately': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'randomize_questions': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class QuizQuestionForm(forms.ModelForm):
    class Meta:
        model = QuizQuestion
        fields = ['question_text', 'question_type', 'marks', 'explanation']
        widgets = {
            'question_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'question_type': forms.Select(attrs={'class': 'form-select'}),
            'marks': forms.NumberInput(attrs={'class': 'form-control'}),
            'explanation': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class QuizOptionForm(forms.ModelForm):
    class Meta:
        model = QuizOption
        fields = ['option_text', 'is_correct']
        widgets = {
            'option_text': forms.TextInput(attrs={'class': 'form-control'}),
            'is_correct': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
