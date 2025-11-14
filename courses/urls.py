from django.urls import path
from . import views

urlpatterns = [
    # Course details
    path('<int:section_id>/', views.course_detail, name='course_detail'),
    
    # Study materials
    path('<int:section_id>/upload-material/', views.upload_material, name='upload_material'),
    path('material/<int:material_id>/download/', views.download_material, name='download_material'),
    path('material/<int:material_id>/delete/', views.delete_material, name='delete_material'),
    
    # Assignments
    path('<int:section_id>/create-assignment/', views.create_assignment, name='create_assignment'),
    path('assignment/<int:assignment_id>/', views.assignment_detail, name='assignment_detail'),
    path('assignment/<int:assignment_id>/edit/', views.edit_assignment, name='edit_assignment'),
    path('assignment/<int:assignment_id>/delete/', views.delete_assignment, name='delete_assignment'),
    path('assignment/<int:assignment_id>/submit/', views.submit_assignment, name='submit_assignment'),
    path('submission/<int:submission_id>/grade/', views.grade_submission, name='grade_submission'),
    
    # Attendance
    path('<int:section_id>/mark-attendance/', views.mark_attendance, name='mark_attendance'),
    path('<int:section_id>/attendance-report/', views.attendance_report, name='attendance_report'),
    
    # Announcements
    path('<int:section_id>/announcements/', views.announcement_list, name='announcement_list'),
    path('<int:section_id>/announcements/create/', views.announcement_create, name='announcement_create'),
    path('announcements/<int:pk>/edit/', views.announcement_edit, name='announcement_edit'),
    path('announcements/<int:pk>/delete/', views.announcement_delete, name='announcement_delete'),
]