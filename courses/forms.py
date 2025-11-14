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
