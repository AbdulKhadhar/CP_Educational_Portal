from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from accounts.models import User
from colleges.models import ClassSection

class StudyMaterial(models.Model):
    MATERIAL_TYPES = (
        ('pdf', 'PDF Document'),
        ('video', 'Video'),
        ('slides', 'Presentation Slides'),
        ('link', 'External Link'),
        ('other', 'Other'),
    )
    
    section = models.ForeignKey(ClassSection, on_delete=models.CASCADE, related_name='materials')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    material_type = models.CharField(max_length=20, choices=MATERIAL_TYPES)
    file = models.FileField(upload_to='study_materials/', blank=True, null=True,
                           validators=[FileExtensionValidator(
                               allowed_extensions=['pdf', 'ppt', 'pptx', 'doc', 'docx', 'mp4', 'avi', 'mkv']
                           )])
    external_link = models.URLField(blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_materials')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    download_count = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.title} - {self.section}"
    
    class Meta:
        ordering = ['-uploaded_at']


class Assignment(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('closed', 'Closed'),
    )
    
    section = models.ForeignKey(ClassSection, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=200)
    description = models.TextField()
    assignment_file = models.FileField(upload_to='assignments/', blank=True, null=True)
    total_marks = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)])
    due_date = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_assignments')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    allow_late_submission = models.BooleanField(default=False)
    late_penalty_percentage = models.IntegerField(default=10, 
                                                  validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    def __str__(self):
        return f"{self.title} - {self.section}"
    
    def is_overdue(self):
        from django.utils import timezone
        return timezone.now() > self.due_date
    
    class Meta:
        ordering = ['-created_at']


class Submission(models.Model):
    STATUS_CHOICES = (
        ('submitted', 'Submitted'),
        ('late', 'Late Submission'),
        ('graded', 'Graded'),
        ('returned', 'Returned for Revision'),
    )
    
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey('colleges.Student', on_delete=models.CASCADE, related_name='submissions')
    submission_file = models.FileField(upload_to='submissions/')
    submission_text = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    feedback = models.TextField(blank=True)
    graded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                 related_name='graded_submissions')
    graded_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.student.roll_number} - {self.assignment.title}"
    
    def calculate_percentage(self):
        if self.marks_obtained and self.assignment.total_marks:
            return round((self.marks_obtained / self.assignment.total_marks) * 100, 2)
        return 0
    
    def is_late(self):
        return self.submitted_at > self.assignment.due_date
    
    class Meta:
        unique_together = ['assignment', 'student']
        ordering = ['-submitted_at']


class Attendance(models.Model):
    STATUS_CHOICES = (
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    )
    
    section = models.ForeignKey(ClassSection, on_delete=models.CASCADE, related_name='attendance_records')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendance_records',
                               limit_choices_to={'role': 'student'})
    date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    remarks = models.TextField(blank=True)
    marked_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='marked_attendance')
    marked_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.section} - {self.date}"
    
    class Meta:
        unique_together = ['section', 'student', 'date']
        ordering = ['-date']


class Announcement(models.Model):
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )
    
    section = models.ForeignKey(ClassSection, on_delete=models.CASCADE, related_name='announcements')
    title = models.CharField(max_length=200)
    content = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='announcements')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    attachment = models.FileField(upload_to='announcements/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.title} - {self.section}"
    
    class Meta:
        ordering = ['-created_at']

