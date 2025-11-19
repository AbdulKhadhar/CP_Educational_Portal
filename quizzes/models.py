from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from accounts.models import User
from colleges.models import ClassSection, Student

class Quiz(models.Model):
    DIFFICULTY_CHOICES = (
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    )
    
    section = models.ForeignKey(ClassSection, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    duration_minutes = models.IntegerField(validators=[MinValueValidator(5), MaxValueValidator(180)])
    total_marks = models.IntegerField(validators=[MinValueValidator(1)])
    passing_marks = models.IntegerField(validators=[MinValueValidator(0)])
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='medium')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    allow_multiple_attempts = models.BooleanField(default=False)
    max_attempts = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    show_results_immediately = models.BooleanField(default=True)
    randomize_questions = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_quizzes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.section}"
    
    def is_available(self):
        now = timezone.now()
        return self.is_active and self.start_time <= now <= self.end_time
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Quizzes'


class QuizQuestion(models.Model):
    QUESTION_TYPES = (
        ('mcq', 'Multiple Choice (Single Answer)'),
        ('multiple', 'Multiple Choice (Multiple Answers)'),
        ('true_false', 'True/False'),
        ('short', 'Short Answer'),
    )
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    marks = models.IntegerField(validators=[MinValueValidator(1)])
    order = models.IntegerField(default=0)
    explanation = models.TextField(blank=True)
    
    def __str__(self):
        return f"Q{self.order}: {self.question_text[:50]}"
    
    class Meta:
        ordering = ['order']


class QuizOption(models.Model):
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE, related_name='options')
    option_text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.option_text[:50]} ({'Correct' if self.is_correct else 'Incorrect'})"
    
    class Meta:
        ordering = ['order']


class QuizAttempt(models.Model):
    STATUS_CHOICES = (
        ('in_progress', 'In Progress'),
        ('submitted', 'Submitted'),
        ('expired', 'Expired'),
    )
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='quiz_attempts')
    attempt_number = models.IntegerField(default=1)
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    time_taken_minutes = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.student.roll_number} - {self.quiz.title} (Attempt {self.attempt_number})"
    
    def calculate_score(self):
        total_score = 0
        total_marks = 0
        
        for answer in self.answers.all():
            total_marks += answer.question.marks
            if answer.is_correct:
                total_score += answer.question.marks
        
        self.score = total_score
        if total_marks > 0:
            self.percentage = round((total_score / total_marks) * 100, 2)
        else:
            self.percentage = 0
        
        self.save()
        return self.score
    
    class Meta:
        ordering = ['-started_at']
        unique_together = ['quiz', 'student', 'attempt_number']


class QuizAnswer(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE, related_name='answers')
    selected_options = models.ManyToManyField(QuizOption, blank=True, related_name='answers')
    text_answer = models.TextField(blank=True)
    is_correct = models.BooleanField(default=False)
    marks_awarded = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    answered_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.attempt.student.roll_number} - Q{self.question.order}"
    
    def check_answer(self):
        if self.question.question_type in ['mcq', 'true_false']:
            correct_options = set(self.question.options.filter(is_correct=True))
            selected_options = set(self.selected_options.all())
            
            if correct_options == selected_options:
                self.is_correct = True
                self.marks_awarded = self.question.marks
            else:
                self.is_correct = False
                self.marks_awarded = 0
        
        self.save()
    
    class Meta:
        unique_together = ['attempt', 'question']


class QuizResult(models.Model):
    attempt = models.OneToOneField(QuizAttempt, on_delete=models.CASCADE, related_name='result')

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='quiz_results')
    enrollment = models.ForeignKey(
        'colleges.Enrollment', 
        on_delete=models.CASCADE, 
        related_name='quiz_results'
    )
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='results')
    score = models.DecimalField(max_digits=5, decimal_places=2)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    passed = models.BooleanField(default=False)
    rank = models.IntegerField(null=True, blank=True)
    completed_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.student.roll_number} - {self.quiz.title}: {self.percentage}%"
    
    class Meta:
        ordering = ['-completed_at']