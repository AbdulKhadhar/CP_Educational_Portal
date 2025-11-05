# courses/forms.py
from django import forms
from .models import StudyMaterial, Assignment, Submission, Attendance, Announcement

class StudyMaterialForm(forms.ModelForm):
    class Meta:
        model = StudyMaterial
        fields = ['title', 'description', 'material_type', 'file', 'external_link']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter description'}),
            'material_type': forms.Select(attrs={'class': 'form-select'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'external_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com'}),
        }

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'assignment_file', 'total_marks', 'due_date', 
                 'status', 'allow_late_submission', 'late_penalty_percentage']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'assignment_file': forms.FileInput(attrs={'class': 'form-control'}),
            'total_marks': forms.NumberInput(attrs={'class': 'form-control'}),
            'due_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'allow_late_submission': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'late_penalty_percentage': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['submission_file', 'submission_text']
        widgets = {
            'submission_file': forms.FileInput(attrs={'class': 'form-control'}),
            'submission_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 
                                                     'placeholder': 'Enter any additional text or comments'}),
        }

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['status', 'remarks']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'remarks': forms.TextInput(attrs={'class': 'form-control'}),
        }

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'content', 'priority', 'attachment']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'attachment': forms.FileInput(attrs={'class': 'form-control'}),
        }


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


# discussions/forms.py
from django import forms
from .models import Discussion, Comment

class DiscussionForm(forms.ModelForm):
    class Meta:
        model = Discussion
        fields = ['title', 'content', 'category', 'attachment']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter discussion title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Write your discussion...'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'attachment': forms.FileInput(attrs={'class': 'form-control'}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content', 'attachment']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Write your comment...'}),
            'attachment': forms.FileInput(attrs={'class': 'form-control'}),
        }


# colleges/forms.py
from django import forms
from .models import Department, Course, ClassSection, Teacher, Student, Enrollment
from accounts.models import User

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'code', 'hod', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'hod': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'code', 'description', 'credits', 'semester']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'credits': forms.NumberInput(attrs={'class': 'form-control'}),
            'semester': forms.Select(attrs={'class': 'form-select'}),
        }

class ClassSectionForm(forms.ModelForm):
    class Meta:
        model = ClassSection
        fields = ['section_name', 'academic_year', 'year', 'teacher', 'max_students']
        widgets = {
            'section_name': forms.TextInput(attrs={'class': 'form-control'}),
            'academic_year': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '2024-2025'}),
            'year': forms.Select(attrs={'class': 'form-select'}),
            'teacher': forms.Select(attrs={'class': 'form-select'}),
            'max_students': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class TeacherForm(forms.ModelForm):
    # User fields
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = Teacher
        fields = ['employee_id', 'qualification', 'specialization', 'joining_date']
        widgets = {
            'employee_id': forms.TextInput(attrs={'class': 'form-control'}),
            'qualification': forms.TextInput(attrs={'class': 'form-control'}),
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
            'joining_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class StudentForm(forms.ModelForm):
    # User fields
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = Student
        fields = ['roll_number', 'admission_year', 'current_semester', 'guardian_name', 'guardian_phone']
        widgets = {
            'roll_number': forms.TextInput(attrs={'class': 'form-control'}),
            'admission_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'current_semester': forms.Select(attrs={'class': 'form-select'}),
            'guardian_name': forms.TextInput(attrs={'class': 'form-control'}),
            'guardian_phone': forms.TextInput(attrs={'class': 'form-control'}),
        }

class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['student', 'section']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'section': forms.Select(attrs={'class': 'form-select'}),
        }