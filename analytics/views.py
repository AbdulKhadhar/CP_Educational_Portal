# analytics/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Avg, Count, Q, F
from django.utils import timezone
from datetime import timedelta

from colleges.models import Student, Department, SPIRecord, Enrollment
from courses.models import Attendance, Assignment, Submission
from quizzes.models import QuizAttempt
from discussions.models import Badge, StudentBadge, Certificate, Discussion

@login_required
def analytics_dashboard(request):
    """Main analytics dashboard"""
    user = request.user
    
    if user.role not in ['college_admin', 'teacher']:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    college = user.college
    
    # Get context based on role
    if user.role == 'college_admin':
        # Overall college stats
        total_students = Student.objects.filter(department__college=college).count()
        total_teachers = college.users.filter(role='teacher').count()
        total_courses = college.departments.aggregate(
            course_count=Count('courses')
        )['course_count'] or 0
        
        # SPI statistics
        spi_stats = SPIRecord.objects.filter(
            student__department__college=college
        ).aggregate(
            avg_spi=Avg('spi_score'),
            high_performers=Count('id', filter=Q(spi_score__gte=80)),
            at_risk=Count('id', filter=Q(spi_score__lt=50))
        )
        
        # Recent activity
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_activity = {
            'assignments_created': Assignment.objects.filter(
                section__course__department__college=college,
                created_at__gte=thirty_days_ago
            ).count(),
            'submissions': Submission.objects.filter(
                assignment__section__course__department__college=college,
                submitted_at__gte=thirty_days_ago
            ).count(),
            'discussions': Discussion.objects.filter(
                section__course__department__college=college,
                created_at__gte=thirty_days_ago
            ).count(),
            'quizzes_taken': QuizAttempt.objects.filter(
                quiz__section__course__department__college=college,
                started_at__gte=thirty_days_ago
            ).count(),
        }
        
        context = {
            'total_students': total_students,
            'total_teachers': total_teachers,
            'total_courses': total_courses,
            'spi_stats': spi_stats,
            'recent_activity': recent_activity,
        }
    
    else:  # teacher
        from colleges.models import ClassSection
        sections = ClassSection.objects.filter(teacher=user)
        
        total_students = sum(section.get_enrolled_count() for section in sections)
        
        # Assignment statistics
        assignment_stats = Assignment.objects.filter(
            section__teacher=user
        ).aggregate(
            total=Count('id'),
            pending_grading=Count('id', filter=Q(submissions__status='submitted'))
        )
        
        # Attendance overview
        attendance_overview = []
        for section in sections:
            total_classes = Attendance.objects.filter(section=section).values('date').distinct().count()
            if total_classes > 0:
                avg_attendance = Attendance.objects.filter(
                    section=section, status='present'
                ).count() / total_classes
                attendance_overview.append({
                    'section': section,
                    'avg_attendance': round(avg_attendance * 100, 2)
                })
        
        context = {
            'sections': sections,
            'total_students': total_students,
            'assignment_stats': assignment_stats,
            'attendance_overview': attendance_overview,
        }
    
    return render(request, 'analytics/dashboard.html', context)

@login_required
def spi_report(request):
    """SPI report for all students"""
    if request.user.role not in ['college_admin', 'teacher']:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    college = request.user.college
    
    # Get all students with their latest SPI
    students = Student.objects.filter(
        department__college=college
    ).select_related('user', 'department')
    
    spi_data = []
    for student in students:
        latest_spi = student.spi_records.order_by('-calculated_date').first()
        current_spi = student.calculate_spi()
        
        spi_data.append({
            'student': student,
            'current_spi': current_spi,
            'latest_record': latest_spi,
            'status': 'high' if current_spi >= 80 else 'at_risk' if current_spi < 50 else 'moderate'
        })
    
    # Sort by SPI descending
    spi_data.sort(key=lambda x: x['current_spi'], reverse=True)
    
    context = {
        'spi_data': spi_data,
    }
    
    return render(request, 'analytics/spi_report.html', context)

@login_required
def participation_report(request):
    """Student participation report"""
    if request.user.role not in ['college_admin', 'teacher']:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    college = request.user.college
    students = Student.objects.filter(department__college=college).select_related('user')
    
    participation_data = []
    for student in students:
        # Count various activities
        assignments_submitted = Submission.objects.filter(student=student).count()
        quizzes_taken = QuizAttempt.objects.filter(student=student, status='submitted').count()
        discussions_participated = Discussion.objects.filter(
            Q(author=student.user) | Q(comments__author=student.user)
        ).distinct().count()
        
        # Calculate attendance
        enrollments = Enrollment.objects.filter(student=student, is_active=True)
        total_classes = 0
        attended_classes = 0
        
        for enrollment in enrollments:
            section_classes = Attendance.objects.filter(
                section=enrollment.section
            ).values('date').distinct().count()
            section_attended = Attendance.objects.filter(
                section=enrollment.section,
                student=student.user,
                status='present'
            ).count()
            
            total_classes += section_classes
            attended_classes += section_attended
        
        attendance_pct = (attended_classes / total_classes * 100) if total_classes > 0 else 0
        
        participation_data.append({
            'student': student,
            'assignments': assignments_submitted,
            'quizzes': quizzes_taken,
            'discussions': discussions_participated,
            'attendance': round(attendance_pct, 2),
        })
    
    context = {
        'participation_data': participation_data,
    }
    
    return render(request, 'analytics/participation_report.html', context)

@login_required
def at_risk_students(request):
    """Identify students at risk (low SPI, attendance, or participation)"""
    if request.user.role not in ['college_admin', 'teacher']:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    college = request.user.college
    students = Student.objects.filter(department__college=college).select_related('user', 'department')
    
    at_risk = []
    for student in students:
        spi = student.calculate_spi()
        
        # Calculate attendance
        enrollments = Enrollment.objects.filter(student=student, is_active=True)
        total_classes = 0
        attended_classes = 0
        
        for enrollment in enrollments:
            section_classes = Attendance.objects.filter(
                section=enrollment.section
            ).values('date').distinct().count()
            section_attended = Attendance.objects.filter(
                section=enrollment.section,
                student=student.user,
                status='present'
            ).count()
            
            total_classes += section_classes
            attended_classes += section_attended
        
        attendance_pct = (attended_classes / total_classes * 100) if total_classes > 0 else 0
        
        # Count recent submissions
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_submissions = Submission.objects.filter(
            student=student,
            submitted_at__gte=thirty_days_ago
        ).count()
        
        # Determine risk factors
        risk_factors = []
        if spi < 50:
            risk_factors.append('Low SPI')
        if attendance_pct < 75:
            risk_factors.append('Low Attendance')
        if recent_submissions == 0:
            risk_factors.append('No Recent Submissions')
        
        if risk_factors:
            at_risk.append({
                'student': student,
                'spi': spi,
                'attendance': round(attendance_pct, 2),
                'recent_submissions': recent_submissions,
                'risk_factors': risk_factors,
            })
    
    # Sort by number of risk factors
    at_risk.sort(key=lambda x: len(x['risk_factors']), reverse=True)
    
    context = {
        'at_risk_students': at_risk,
    }
    
    return render(request, 'analytics/at_risk_students.html', context)

# API Endpoints for Chart.js

@login_required
def api_spi_distribution(request):
    """API endpoint for SPI distribution chart"""
    college = request.user.college
    
    # Get SPI ranges
    spi_ranges = {
        '0-40': 0,
        '40-50': 0,
        '50-60': 0,
        '60-70': 0,
        '70-80': 0,
        '80-90': 0,
        '90-100': 0,
    }
    
    students = Student.objects.filter(department__college=college)
    for student in students:
        spi = student.calculate_spi()
        if spi < 40:
            spi_ranges['0-40'] += 1
        elif spi < 50:
            spi_ranges['40-50'] += 1
        elif spi < 60:
            spi_ranges['50-60'] += 1
        elif spi < 70:
            spi_ranges['60-70'] += 1
        elif spi < 80:
            spi_ranges['70-80'] += 1
        elif spi < 90:
            spi_ranges['80-90'] += 1
        else:
            spi_ranges['90-100'] += 1
    
    return JsonResponse({
        'labels': list(spi_ranges.keys()),
        'data': list(spi_ranges.values()),
    })

@login_required
def api_attendance_trends(request):
    """API endpoint for attendance trends over time"""
    college = request.user.college
    
    # Get last 30 days attendance
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    
    attendance_by_date = Attendance.objects.filter(
        section__course__department__college=college,
        date__gte=thirty_days_ago
    ).values('date').annotate(
        present_count=Count('id', filter=Q(status='present')),
        total_count=Count('id')
    ).order_by('date')
    
    labels = []
    percentages = []
    
    for record in attendance_by_date:
        labels.append(record['date'].strftime('%m/%d'))
        if record['total_count'] > 0:
            percentage = (record['present_count'] / record['total_count']) * 100
        else:
            percentage = 0
        percentages.append(round(percentage, 2))
    
    return JsonResponse({
        'labels': labels,
        'data': percentages,
    })

@login_required
def api_engagement_overview(request):
    """API endpoint for overall engagement metrics"""
    college = request.user.college
    
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    # Count various activities
    assignments_count = Assignment.objects.filter(
        section__course__department__college=college,
        created_at__gte=thirty_days_ago
    ).count()
    
    submissions_count = Submission.objects.filter(
        assignment__section__course__department__college=college,
        submitted_at__gte=thirty_days_ago
    ).count()
    
    quizzes_count = QuizAttempt.objects.filter(
        quiz__section__course__department__college=college,
        started_at__gte=thirty_days_ago,
        status='submitted'
    ).count()
    
    discussions_count = Discussion.objects.filter(
        section__course__department__college=college,
        created_at__gte=thirty_days_ago
    ).count()
    
    return JsonResponse({
        'labels': ['Assignments', 'Submissions', 'Quizzes', 'Discussions'],
        'data': [assignments_count, submissions_count, quizzes_count, discussions_count],
    })

@login_required
def api_department_performance(request):
    """API endpoint for department-wise performance"""
    college = request.user.college
    
    departments = Department.objects.filter(college=college)
    
    labels = []
    avg_spis = []
    
    for dept in departments:
        labels.append(dept.name)
        
        students = Student.objects.filter(department=dept)
        if students.exists():
            total_spi = sum(student.calculate_spi() for student in students)
            avg_spi = total_spi / students.count()
        else:
            avg_spi = 0
        
        avg_spis.append(round(avg_spi, 2))
    
    return JsonResponse({
        'labels': labels,
        'data': avg_spis,
    })

# Badge Management

@login_required
def badge_list(request):
    """List all badges"""
    badges = Badge.objects.filter(is_active=True)
    
    if request.user.role == 'student':
        try:
            student = Student.objects.get(user=request.user)
            earned_badges = StudentBadge.objects.filter(student=student).select_related('badge')
        except Student.DoesNotExist:
            earned_badges = []
    else:
        earned_badges = []
    
    context = {
        'badges': badges,
        'earned_badges': earned_badges,
    }
    
    return render(request, 'analytics/badge_list.html', context)

@login_required
def award_badge(request):
    """Award badge to a student"""
    if request.user.role not in ['college_admin', 'teacher']:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        badge_id = request.POST.get('badge_id')
        reason = request.POST.get('reason', '')
        
        student = get_object_or_404(Student, pk=student_id)
        badge = get_object_or_404(Badge, pk=badge_id)
        
        StudentBadge.objects.get_or_create(
            student=student,
            badge=badge,
            defaults={'reason': reason}
        )
        
        messages.success(request, f'Badge "{badge.name}" awarded to {student.user.get_full_name()}!')
        return redirect('badge_list')
    
    college = request.user.college
    students = Student.objects.filter(department__college=college).select_related('user')
    badges = Badge.objects.filter(is_active=True)
    
    return render(request, 'analytics/award_badge.html', {'students': students, 'badges': badges})

# Certificate Management

@login_required
def certificate_list(request):
    """List certificates"""
    if request.user.role == 'student':
        try:
            student = Student.objects.get(user=request.user)
            certificates = Certificate.objects.filter(student=student)
        except Student.DoesNotExist:
            certificates = []
    else:
        college = request.user.college
        certificates = Certificate.objects.filter(
            student__department__college=college
        ).select_related('student')
    
    return render(request, 'analytics/certificate_list.html', {'certificates': certificates})

@login_required
def generate_certificate(request):
    """Generate certificate for a student"""
    if request.user.role not in ['college_admin', 'teacher']:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        certificate_type = request.POST.get('certificate_type')
        title = request.POST.get('title')
        description = request.POST.get('description')
        
        student = get_object_or_404(Student, pk=student_id)
        
        certificate = Certificate.objects.create(
            student=student,
            certificate_type=certificate_type,
            title=title,
            description=description,
            issued_by=request.user
        )
        
        messages.success(request, f'Certificate generated successfully! Number: {certificate.certificate_number}')
        return redirect('certificate_list')
    
    college = request.user.college
    students = Student.objects.filter(department__college=college).select_related('user')
    
    return render(request, 'analytics/generate_certificate.html', {'students': students})

@login_required
def view_certificate(request, cert_number):
    """View certificate details"""
    certificate = get_object_or_404(Certificate, certificate_number=cert_number)
    
    # Check access
    if request.user.role == 'student':
        if certificate.student.user != request.user:
            messages.error(request, 'Access denied.')
            return redirect('dashboard')
    
    return render(request, 'analytics/view_certificate.html', {'certificate': certificate})

# Peer Group Management

@login_required
def peer_group_list(request):
    """List peer groups"""
    if request.user.role == 'student':
        try:
            student = Student.objects.get(user=request.user)
            groups = student.peer_groups.filter(is_active=True)
        except Student.DoesNotExist:
            groups = []
    else:
        college = request.user.college
        groups = PeerGroup.objects.filter(
            section__course__department__college=college,
            is_active=True
        )
    
    return render(request, 'analytics/peer_group_list.html', {'groups': groups})

@login_required
def peer_group_create(request):
    """Create a new peer group"""
    # Implementation here
    pass

@login_required
def peer_group_detail(request, pk):
    """Peer group detail view"""
    group = get_object_or_404(PeerGroup, pk=pk)
    
    # Check access
    if request.user.role == 'student':
        try:
            student = Student.objects.get(user=request.user)
            if student not in group.members.all():
                messages.error(request, 'Access denied.')
                return redirect('peer_group_list')
        except Student.DoesNotExist:
            messages.error(request, 'Student profile not found.')
            return redirect('dashboard')
    
    activities = group.activities.order_by('-scheduled_date')
    
    return render(request, 'analytics/peer_group_detail.html', {'group': group, 'activities': activities})