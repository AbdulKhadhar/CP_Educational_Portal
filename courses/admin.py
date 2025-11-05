# courses/admin.py
from django.contrib import admin
from .models import StudyMaterial, Assignment, Submission, Attendance, Announcement

@admin.register(StudyMaterial)
class StudyMaterialAdmin(admin.ModelAdmin):
    list_display = ['title', 'section', 'material_type', 'uploaded_by', 'uploaded_at', 'download_count']
    list_filter = ['material_type', 'uploaded_at', 'is_active']
    search_fields = ['title', 'section__course__name']
    raw_id_fields = ['section', 'uploaded_by']

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'section', 'total_marks', 'due_date', 'status', 'created_by']
    list_filter = ['status', 'due_date', 'created_at']
    search_fields = ['title', 'section__course__name']
    raw_id_fields = ['section', 'created_by']

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['assignment', 'student', 'status', 'marks_obtained', 'submitted_at', 'graded_by']
    list_filter = ['status', 'submitted_at', 'graded_at']
    search_fields = ['assignment__title', 'student__roll_number']
    raw_id_fields = ['assignment', 'student', 'graded_by']

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['section', 'student', 'date', 'status', 'marked_by']
    list_filter = ['status', 'date', 'section']
    search_fields = ['student__username', 'section__course__name']
    raw_id_fields = ['section', 'student', 'marked_by']
    date_hierarchy = 'date'

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'section', 'priority', 'created_by', 'created_at', 'is_active']
    list_filter = ['priority', 'is_active', 'created_at']
    search_fields = ['title', 'content', 'section__course__name']
    raw_id_fields = ['section', 'created_by']