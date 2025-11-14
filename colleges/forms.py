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