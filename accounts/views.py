from django.shortcuts import render

# Create your views here.
# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Avg, Q
from .models import User
from colleges.models import Student, Teacher, Department, ClassSection
from courses.models import Assignment, Submission, Attendance
from quizzes.models import Quiz, QuizAttempt

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name()}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'accounts/login.html')

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('login')

@login_required
def dashboard(request):
    user = request.user
    context = {'user': user}
    
    if user.role == 'college_admin':
        return redirect('admin_dashboard')
    elif user.role == 'teacher':
        return redirect('teacher_dashboard')
    elif user.role == 'student':
        return redirect('student_dashboard')
    else:
        return redirect('login')

@login_required
def admin_dashboard(request):
    if request.user.role != 'college_admin':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    college = request.user.college
    
    # Statistics
    total_departments = Department.objects.filter(college=college).count()
    total_teachers = Teacher.objects.filter(department__college=college).count()
    total_students = Student.objects.filter(department__college=college).count()
    total_sections = ClassSection.objects.filter(course__department__college=college).count()
    
    # Recent activities
    recent_students = Student.objects.filter(
        department__college=college
    ).select_related('user', 'department').order_by('-user__date_joined')[:5]
    
    # Department-wise student count
    dept_stats = Department.objects.filter(college=college).annotate(
        student_count=Count('students')
    ).values('name', 'student_count')
    
    # SPI Statistics
    from colleges.models import SPIRecord
    spi_stats = SPIRecord.objects.filter(
        student__department__college=college
    ).aggregate(
        avg_spi=Avg('spi_score'),
        high_performers=Count('id', filter=Q(spi_score__gte=80)),
        at_risk=Count('id', filter=Q(spi_score__lt=50))
    )
    
    context = {
        'total_departments': total_departments,
        'total_teachers': total_teachers,
        'total_students': total_students,
        'total_sections': total_sections,
        'recent_students': recent_students,
        'dept_stats': list(dept_stats),
        'spi_stats': spi_stats,
    }
    
    return render(request, 'admin/dashboard.html', context)

@login_required
def teacher_dashboard(request):
    if request.user.role != 'teacher':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    try:
        teacher = Teacher.objects.get(user=request.user)
    except Teacher.DoesNotExist:
        messages.error(request, 'Teacher profile not found.')
        return redirect('dashboard')
    
    # Get assigned sections
    sections = ClassSection.objects.filter(teacher=request.user).select_related('course')
    
    # Statistics
    total_sections = sections.count()
    total_students = sum(section.get_enrolled_count() for section in sections)
    
    # Pending assignments to grade
    pending_submissions = Submission.objects.filter(
        assignment__section__teacher=request.user,
        status='submitted'
    ).count()
    
    # Recent activities
    recent_submissions = Submission.objects.filter(
        assignment__section__teacher=request.user
    ).select_related('student', 'assignment').order_by('-submitted_at')[:5]
    
    # Upcoming quizzes
    from django.utils import timezone
    upcoming_quizzes = Quiz.objects.filter(
        section__teacher=request.user,
        start_time__gte=timezone.now()
    ).order_by('start_time')[:5]
    
    context = {
        'teacher': teacher,
        'sections': sections,
        'total_sections': total_sections,
        'total_students': total_students,
        'pending_submissions': pending_submissions,
        'recent_submissions': recent_submissions,
        'upcoming_quizzes': upcoming_quizzes,
    }
    
    return render(request, 'teacher/dashboard.html', context)

@login_required
def student_dashboard(request):
    if request.user.role != 'student':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('dashboard')
    
    # Get enrolled sections
    from colleges.models import Enrollment
    enrollments = Enrollment.objects.filter(
        student=student, is_active=True
    ).select_related('section__course')
    
    # Calculate SPI
    spi_score = student.calculate_spi()
    
    # Statistics
    total_courses = enrollments.count()
    
    # Pending assignments
    from django.utils import timezone
    pending_assignments = Assignment.objects.filter(
        section__enrollments__student=student,
        status='published',
        due_date__gte=timezone.now()
    ).exclude(
        submissions__student=student
    ).count()
    
    # Recent submissions
    recent_submissions = Submission.objects.filter(
        student=student
    ).select_related('assignment').order_by('-submitted_at')[:5]
    
    # Upcoming quizzes
    upcoming_quizzes = Quiz.objects.filter(
        section__enrollments__student=student,
        start_time__gte=timezone.now(),
        is_active=True
    ).order_by('start_time')[:5]
    
    # Attendance percentage
    attendance_stats = {}
    for enrollment in enrollments:
        total_classes = Attendance.objects.filter(
            section=enrollment.section
        ).values('date').distinct().count()
        
        attended = Attendance.objects.filter(
            section=enrollment.section,
            student=request.user,
            status='present'
        ).count()
        
        if total_classes > 0:
            percentage = round((attended / total_classes) * 100, 2)
        else:
            percentage = 0
        
        attendance_stats[enrollment.section.id] = {
            'attended': attended,
            'total': total_classes,
            'percentage': percentage
        }
    
    # Recent badges
    from discussions.models import StudentBadge
    recent_badges = StudentBadge.objects.filter(
        student=student
    ).select_related('badge').order_by('-earned_date')[:3]
    
    context = {
        'student': student,
        'enrollments': enrollments,
        'spi_score': spi_score,
        'total_courses': total_courses,
        'pending_assignments': pending_assignments,
        'recent_submissions': recent_submissions,
        'upcoming_quizzes': upcoming_quizzes,
        'attendance_stats': attendance_stats,
        'recent_badges': recent_badges,
    }
    
    return render(request, 'student/dashboard.html', context)

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {'user': request.user})