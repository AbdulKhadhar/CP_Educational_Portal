# colleges/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Department management
    path('departments/', views.department_list, name='department_list'),
    path('departments/create/', views.department_create, name='department_create'),
    path('departments/<int:pk>/edit/', views.department_edit, name='department_edit'),
    path('departments/<int:pk>/delete/', views.department_delete, name='department_delete'),
    
    # Course management
    path('courses/', views.course_list, name='course_list'),
    path('courses/create/<int:dept_id>/', views.course_create, name='course_create'),
    path('courses/<int:pk>/edit/', views.course_edit, name='course_edit'),
    path('courses/<int:pk>/delete/', views.course_delete, name='course_delete'),
    
    # Section management
    path('sections/', views.section_list, name='section_list'),
    path('sections/create/<int:course_id>/', views.section_create, name='section_create'),
    path('sections/<int:pk>/edit/', views.section_edit, name='section_edit'),
    path('sections/<int:pk>/delete/', views.section_delete, name='section_delete'),
    
    # Teacher management
    path('teachers/', views.teacher_list, name='teacher_list'),
    path('teachers/register/', views.teacher_register, name='teacher_register'),
    path('teachers/<int:pk>/edit/', views.teacher_edit, name='teacher_edit'),
    path('teachers/<int:pk>/delete/', views.teacher_delete, name='teacher_delete'),
    
    # Student management
    path('students/', views.student_list, name='student_list'),
    path('students/register/', views.student_register, name='student_register'),
    path('students/<int:pk>/edit/', views.student_edit, name='student_edit'),
    path('students/<int:pk>/delete/', views.student_delete, name='student_delete'),
    path('students/<int:pk>/details/', views.student_details, name='student_details'),
    
    # Enrollment
    path('enrollments/', views.enrollment_list, name='enrollment_list'),
    path('enrollments/create/', views.enrollment_create, name='enrollment_create'),
    path('enrollments/<int:pk>/delete/', views.enrollment_delete, name='enrollment_delete'),
    path('enrollments/bulk-enroll/', views.bulk_enroll_existing_students, name='bulk_enroll_existing_students'),
]