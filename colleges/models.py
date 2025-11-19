from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

from accounts.models import College, User

# colleges/models.py
class Department(models.Model):
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='departments')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)
    hod = models.ForeignKey(
        'Teacher', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='headed_department' 
    )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.college.name}"
    
    class Meta:
        unique_together = ['college', 'code']
        ordering = ['name']


class Course(models.Model):
    SEMESTER_CHOICES = [(i, f"Semester {i}") for i in range(1, 9)]
    
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    credits = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    semester = models.IntegerField(choices=SEMESTER_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    class Meta:
        unique_together = ['department', 'code']
        ordering = ['semester', 'name']


class ClassSection(models.Model):
    YEAR_CHOICES = [(i, f"Year {i}") for i in range(1, 5)]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sections')
    section_name = models.CharField(max_length=10)  # A, B, C, etc.
    academic_year = models.CharField(max_length=9)  # 2024-2025
    year = models.IntegerField(choices=YEAR_CHOICES)
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, 
                               related_name='teaching_sections', limit_choices_to={'role': 'teacher'})
    max_students = models.IntegerField(default=60)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.course.code} - Section {self.section_name} ({self.academic_year})"
    
    def get_enrolled_count(self):
        return self.enrollments.count()
    
    class Meta:
        unique_together = ['course', 'section_name', 'academic_year']
        ordering = ['course', 'section_name']


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, 
                               limit_choices_to={'role': 'teacher'})
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='teachers')
    employee_id = models.CharField(max_length=20, unique=True)
    qualification = models.CharField(max_length=100)
    specialization = models.CharField(max_length=200)
    joining_date = models.DateField()
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.employee_id}"
    
    class Meta:
        ordering = ['user__first_name']


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, 
                               limit_choices_to={'role': 'student'})
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='students')
    roll_number = models.CharField(max_length=20, unique=True)
    admission_year = models.IntegerField()
    current_semester = models.IntegerField(
        choices=Course.SEMESTER_CHOICES, # Reuse the choices list
        validators=[MinValueValidator(1), MaxValueValidator(8)]
    )
    guardian_name = models.CharField(max_length=100)
    guardian_phone = models.CharField(max_length=15)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.roll_number}"
    
    def calculate_spi(self):
        """Calculate Student Participation Index (SPI)"""
        from django.db.models import Avg
        
        # Get all enrollments for current semester
        enrollments = self.enrollments.filter(
            section__course__semester=self.current_semester
        )
        
        if not enrollments.exists():
            return Decimal('0.0') # Return Decimal('0.0') instead of integer 0
        
        total_spi = Decimal('0.0')
        enrollment_count = enrollments.count()

        # Define weights as Decimal constants for precise calculation
        WEIGHT_ASSIGNMENT = Decimal('0.4')
        WEIGHT_QUIZ = Decimal('0.3')
        WEIGHT_ATTENDANCE = Decimal('0.2')
        WEIGHT_FORUM = Decimal('0.1')
        
        for enrollment in enrollments:
            
            # --- 1. Assignment score (40%) ---
            assignment_avg = enrollment.submissions.filter(
                status='graded'
            ).aggregate(Avg('marks_obtained'))['marks_obtained__avg']
            # Convert to Decimal, defaulting to 0.0 if None
            assignment_avg = Decimal(assignment_avg) if assignment_avg is not None else Decimal('0.0')
            
            # --- 2. Quiz score (30%) ---
            quiz_avg = enrollment.quiz_results.aggregate(
                Avg('percentage')
            )['percentage__avg']
            # Convert to Decimal, defaulting to 0.0 if None
            quiz_avg = Decimal(quiz_avg) if quiz_avg is not None else Decimal('0.0')

            # --- 3. Attendance (20%) ---
            total_classes = enrollment.section.attendance_records.values('date').distinct().count()
            attended_classes = enrollment.section.attendance_records.filter(
                student=self.user, status='present'
            ).count()
            
            if total_classes > 0:
                # 🛑 THE FIX: Convert at least one integer to Decimal BEFORE division
                attendance_pct = (Decimal(attended_classes) / Decimal(total_classes)) * Decimal('100.0')
            else:
                attendance_pct = Decimal('0.0')
            
            # Ensure attendance_pct is a Decimal (it should be due to the Decimal('100.0') multiplication)

            # --- 4. Forum participation (10%) ---
            forum_count = enrollment.section.discussions.filter(
                models.Q(comments__author=self.user) | models.Q(author=self.user)
            ).distinct().count()
            # Forum score calculation should result in a Decimal
            forum_score = min(Decimal(forum_count * 10), Decimal('100.0'))
            
            # --- 5. Calculate weighted course SPI ---
            # All operands are now Decimal objects, resolving the TypeError
            course_spi = (
                (WEIGHT_ASSIGNMENT * assignment_avg) +
                (WEIGHT_QUIZ * quiz_avg) +
                (WEIGHT_ATTENDANCE * attendance_pct) +
                (WEIGHT_FORUM * forum_score)
            )
            total_spi += course_spi
        
        # Calculate final semester SPI and round to 2 decimal places
        final_spi = total_spi / Decimal(enrollment_count)
        
        # Rounding should be applied carefully when using Decimal.
        # Python's round() can convert Decimal back to float. 
        # Use quantize for Decimal rounding.
        return final_spi.quantize(Decimal('0.01'))
    
    class Meta:
        ordering = ['roll_number']


class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    section = models.ForeignKey(ClassSection, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.student.roll_number} - {self.section}"
    
    class Meta:
        unique_together = ['student', 'section']
        ordering = ['enrolled_date']


class SPIRecord(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='spi_records')
    semester = models.IntegerField()
    spi_score = models.DecimalField(max_digits=5, decimal_places=2)
    calculated_date = models.DateField(auto_now=True)
    assignment_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    quiz_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    attendance_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    forum_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    def __str__(self):
        return f"{self.student.roll_number} - Sem {self.semester}: {self.spi_score}"
    
    class Meta:
        unique_together = ['student', 'semester', 'calculated_date']
        ordering = ['-calculated_date']