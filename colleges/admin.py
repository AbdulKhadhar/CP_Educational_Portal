# colleges/admin.py
from django.contrib import admin
from .models import Department, Course, ClassSection, Teacher, Student, Enrollment, SPIRecord

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'college', 'hod', 'created_at']
    list_filter = ['college', 'created_at']
    search_fields = ['name', 'code']
    raw_id_fields = ['hod']

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'department', 'credits', 'semester']
    list_filter = ['department', 'semester', 'credits']
    search_fields = ['name', 'code']

@admin.register(ClassSection)
class ClassSectionAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'course', 'teacher', 'academic_year', 'get_enrolled_count', 'max_students']
    list_filter = ['course__department', 'academic_year', 'year']
    search_fields = ['section_name', 'course__name', 'course__code']
    raw_id_fields = ['teacher']

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['user', 'employee_id', 'department', 'qualification', 'joining_date']
    list_filter = ['department', 'qualification', 'joining_date']
    search_fields = ['user__first_name', 'user__last_name', 'employee_id']
    raw_id_fields = ['user']

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['user', 'roll_number', 'department', 'current_semester', 'admission_year']
    list_filter = ['department', 'current_semester', 'admission_year']
    search_fields = ['user__first_name', 'user__last_name', 'roll_number']
    raw_id_fields = ['user']

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'section', 'enrolled_date', 'is_active']
    list_filter = ['is_active', 'enrolled_date', 'section__course__department']
    search_fields = ['student__roll_number', 'section__course__name']
    raw_id_fields = ['student', 'section']

@admin.register(SPIRecord)
class SPIRecordAdmin(admin.ModelAdmin):
    list_display = ['student', 'semester', 'spi_score', 'calculated_date']
    list_filter = ['semester', 'calculated_date']
    search_fields = ['student__roll_number', 'student__user__first_name']
    raw_id_fields = ['student']
