from django.urls import path
from . import views

urlpatterns = [
    # Analytics dashboard
    path('', views.analytics_dashboard, name='analytics_dashboard'),
    path('spi-report/', views.spi_report, name='spi_report'),
    path('participation-report/', views.participation_report, name='participation_report'),
    path('at-risk-students/', views.at_risk_students, name='at_risk_students'),
    
    # API endpoints for Chart.js
    path('api/spi-distribution/', views.api_spi_distribution, name='api_spi_distribution'),
    path('api/attendance-trends/', views.api_attendance_trends, name='api_attendance_trends'),
    path('api/engagement-overview/', views.api_engagement_overview, name='api_engagement_overview'),
    path('api/department-performance/', views.api_department_performance, name='api_department_performance'),
    
    # Badges & Certificates
    path('badges/', views.badge_list, name='badge_list'),
    path('badges/award/', views.award_badge, name='award_badge'),
    path('certificates/', views.certificate_list, name='certificate_list'),
    path('certificates/generate/', views.generate_certificate, name='generate_certificate'),
    path('certificates/<str:cert_number>/', views.view_certificate, name='view_certificate'),
    
    # Peer groups
    path('peer-groups/', views.peer_group_list, name='peer_group_list'),
    path('peer-groups/create/', views.peer_group_create, name='peer_group_create'),
    path('peer-groups/<int:pk>/', views.peer_group_detail, name='peer_group_detail'),
]