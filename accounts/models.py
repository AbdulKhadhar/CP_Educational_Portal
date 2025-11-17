# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class College(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    address = models.TextField()
    established_year = models.IntegerField()
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class User(AbstractUser):
    ROLE_CHOICES = (
        ('college_admin', 'College Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    college = models.ForeignKey(College, on_delete=models.CASCADE, null=True, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
    
    class Meta:
        ordering = ['first_name', 'last_name']
