# courses/views.py - COMPLETE
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import FileResponse
from django.db.models import Q
from .models import StudyMaterial, Assignment, Submission, Attendance, Announcement
from colleges.models import ClassSection, Student, Enrollment
from .forms import StudyMaterialForm, AssignmentForm, SubmissionForm, AttendanceForm, AnnouncementForm

@login_required
def course_detail(request, section_id):
    section = get_object_or_404(ClassSection, id=section_id)
    
    # Check access
    if request.user.role == 'student':
        if not Enrollment.objects.filter(student__user=request.user, section=section, is_active=True).exists():
            messages.error(request, 'You are not enrolled in this course.')
            return redirect('student_dashboard')
    elif request.user.role == 'teacher':
        if section.teacher != request.user:
            messages.error(request, 'You do not have access to this course.')
            return redirect('teacher_dashboard')
    
    materials = StudyMaterial.objects.filter(section=section, is_active=True).order_by('-uploaded_at')
    
    if request.user.role == 'teacher':
        assignments = Assignment.objects.filter(section=section).order_by('-created_at')
    else:
        assignments = Assignment.objects.filter(section=section, status='published').order_by('-created_at')
    
    announcements = Announcement.objects.filter(section=section, is_active=True).order_by('-created_at')[:5]
    
    context = {
        'section': section,
        'materials': materials,
        'assignments': assignments,
        'announcements': announcements,
    }
    
    return render(request, 'courses/course_detail.html', context)

@login_required
def upload_material(request, section_id):
    if request.user.role != 'teacher':
        messages.error(request, 'Only teachers can upload materials.')
        return redirect('dashboard')
    
    section = get_object_or_404(ClassSection, id=section_id, teacher=request.user)
    
    if request.method == 'POST':
        form = StudyMaterialForm(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.section = section
            material.uploaded_by = request.user
            material.save()
            messages.success(request, 'Study material uploaded successfully!')
            return redirect('course_detail', section_id=section.id)
    else:
        form = StudyMaterialForm()
    
    return render(request, 'courses/upload_material.html', {'form': form, 'section': section})

@login_required
def download_material(request, material_id):
    material = get_object_or_404(StudyMaterial, id=material_id)
    
    if request.user.role == 'student':
        if not Enrollment.objects.filter(student__user=request.user, section=material.section, is_active=True).exists():
            messages.error(request, 'Access denied.')
            return redirect('student_dashboard')
    
    material.download_count += 1
    material.save()
    
    return FileResponse(material.file.open('rb'), as_attachment=True)

@login_required
def delete_material(request, material_id):
    if request.user.role != 'teacher':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    material = get_object_or_404(StudyMaterial, id=material_id, uploaded_by=request.user)
    
    if request.method == 'POST':
        section_id = material.section.id
        material.delete()
        messages.success(request, 'Material deleted successfully!')
        return redirect('course_detail', section_id=section_id)
    
    return render(request, 'courses/material_confirm_delete.html', {'material': material})

@login_required
def create_assignment(request, section_id):
    if request.user.role != 'teacher':
        messages.error(request, 'Only teachers can create assignments.')
        return redirect('dashboard')
    
    section = get_object_or_404(ClassSection, id=section_id, teacher=request.user)
    
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.section = section
            assignment.created_by = request.user
            assignment.save()
            messages.success(request, 'Assignment created successfully!')
            return redirect('course_detail', section_id=section.id)
    else:
        form = AssignmentForm()
    
    return render(request, 'courses/create_assignment.html', {'form': form, 'section': section})

@login_required
def assignment_detail(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    
    if request.user.role == 'student':
        if not Enrollment.objects.filter(student__user=request.user, section=assignment.section, is_active=True).exists():
            messages.error(request, 'Access denied.')
            return redirect('student_dashboard')
        
        try:
            submission = Submission.objects.get(assignment=assignment, student__user=request.user)
        except Submission.DoesNotExist:
            submission = None
        
        context = {
            'assignment': assignment,
            'submission': submission,
            'can_submit': not assignment.is_overdue() or assignment.allow_late_submission,
        }
        
        return render(request, 'courses/assignment_detail_student.html', context)
    
    elif request.user.role == 'teacher':
        submissions = Submission.objects.filter(assignment=assignment).select_related('student__user')
        
        total_students = assignment.section.get_enrolled_count()
        submitted_count = submissions.count()
        graded_count = submissions.filter(status='graded').count()
        pending_count = submissions.filter(status='submitted').count()
        
        context = {
            'assignment': assignment,
            'submissions': submissions,
            'total_students': total_students,
            'submitted_count': submitted_count,
            'graded_count': graded_count,
            'pending_count': pending_count,
        }
        
        return render(request, 'courses/assignment_detail_teacher.html', context)

@login_required
def edit_assignment(request, assignment_id):
    if request.user.role != 'teacher':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    assignment = get_object_or_404(Assignment, id=assignment_id, created_by=request.user)
    
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES, instance=assignment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Assignment updated successfully!')
            return redirect('assignment_detail', assignment_id=assignment.id)
    else:
        form = AssignmentForm(instance=assignment)
    
    return render(request, 'courses/create_assignment.html', {
        'form': form,
        'section': assignment.section,
        'action': 'Edit'
    })

@login_required
def delete_assignment(request, assignment_id):
    if request.user.role != 'teacher':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    assignment = get_object_or_404(Assignment, id=assignment_id, created_by=request.user)
    
    if request.method == 'POST':
        section_id = assignment.section.id
        assignment.delete()
        messages.success(request, 'Assignment deleted successfully!')
        return redirect('course_detail', section_id=section_id)
    
    return render(request, 'courses/assignment_confirm_delete.html', {'assignment': assignment})

@login_required
def submit_assignment(request, assignment_id):
    # 1. Access Control
    if request.user.role != 'student':
        messages.error(request, 'Only students can submit assignments.')
        return redirect('dashboard')
    
    assignment = get_object_or_404(Assignment, id=assignment_id)
    student = get_object_or_404(Student, user=request.user)
    
    # 2. Enrollment Check & Fetch (Required to set submission.enrollment)
    try:
        # Fetch the specific Enrollment object linking the student to this assignment's section
        enrollment = Enrollment.objects.get(
            student=student, 
            section=assignment.section, 
            is_active=True
        )
    except Enrollment.DoesNotExist:
        messages.error(request, 'You are not enrolled in the course associated with this assignment.')
        return redirect('student_dashboard')

    # 3. Duplicate Submission Check
    # Check using both 'assignment' and the fetched 'enrollment' for maximum integrity.
    if Submission.objects.filter(assignment=assignment, enrollment=enrollment).exists():
        messages.warning(request, 'You have already submitted this assignment.')
        return redirect('assignment_detail', assignment_id=assignment.id)
    
    # 4. Deadline Check
    if assignment.is_overdue() and not assignment.allow_late_submission:
        messages.error(request, 'Submission deadline has passed.')
        return redirect('assignment_detail', assignment_id=assignment.id)
    
    # 5. POST Request Handling
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            
            # 🛑 THE INTEGRITY FIXES: Setting mandatory Foreign Keys
            submission.assignment = assignment
            submission.student = student       # Fixes NOT NULL constraint failed: courses_submission.student_id
            submission.enrollment = enrollment # Fixes NOT NULL constraint failed: courses_submission.enrollment_id
            
            # 6. Status Logic
            if assignment.is_overdue():
                submission.status = 'late'
            else:
                submission.status = 'submitted'
            
            # 7. Save and Redirect
            submission.save()
            messages.success(request, 'Assignment submitted successfully!')
            return redirect('assignment_detail', assignment_id=assignment.id)
    else:
        form = SubmissionForm()
    
    return render(request, 'courses/submit_assignment.html', {'form': form, 'assignment': assignment})

@login_required
def grade_submission(request, submission_id):
    if request.user.role != 'teacher':
        messages.error(request, 'Only teachers can grade submissions.')
        return redirect('dashboard')
    
    submission = get_object_or_404(Submission, id=submission_id)
    
    if submission.assignment.section.teacher != request.user:
        messages.error(request, 'Access denied.')
        return redirect('teacher_dashboard')
    
    if request.method == 'POST':
        marks = request.POST.get('marks_obtained')
        feedback = request.POST.get('feedback')
        
        submission.marks_obtained = marks
        submission.feedback = feedback
        submission.status = 'graded'
        submission.graded_by = request.user
        submission.graded_at = timezone.now()
        submission.save()
        
        messages.success(request, f'Submission graded successfully! Marks: {marks}/{submission.assignment.total_marks}')
        return redirect('assignment_detail', assignment_id=submission.assignment.id)
    
    return render(request, 'courses/grade_submission.html', {'submission': submission})

@login_required
def mark_attendance(request, section_id):
    if request.user.role != 'teacher':
        messages.error(request, 'Only teachers can mark attendance.')
        return redirect('dashboard')
    
    section = get_object_or_404(ClassSection, id=section_id, teacher=request.user)
    
    if request.method == 'POST':
        date = request.POST.get('date')
        students = Enrollment.objects.filter(section=section, is_active=True).select_related('student__user')
        
        for enrollment in students:
            status = request.POST.get(f'status_{enrollment.student.user.id}')
            remarks = request.POST.get(f'remarks_{enrollment.student.user.id}', '')
            
            if status:
                Attendance.objects.update_or_create(
                    section=section,
                    student=enrollment.student.user,
                    date=date,
                    defaults={
                        'status': status,
                        'remarks': remarks,
                        'marked_by': request.user
                    }
                )
        
        messages.success(request, 'Attendance marked successfully!')
        return redirect('course_detail', section_id=section.id)
    
    enrollments = Enrollment.objects.filter(section=section, is_active=True).select_related('student__user')
    today = timezone.now().date()
    
    context = {
        'section': section,
        'enrollments': enrollments,
        'today': today,
    }
    
    return render(request, 'courses/mark_attendance.html', context)

@login_required
def attendance_report(request, section_id):
    section = get_object_or_404(ClassSection, id=section_id)
    
    if request.user.role == 'teacher' and section.teacher != request.user:
        messages.error(request, 'Access denied.')
        return redirect('teacher_dashboard')
    
    enrollments = Enrollment.objects.filter(section=section, is_active=True).select_related('student__user')
    
    attendance_data = []
    for enrollment in enrollments:
        total_classes = Attendance.objects.filter(section=section).values('date').distinct().count()
        attended = Attendance.objects.filter(section=section, student=enrollment.student.user, status='present').count()
        absent = Attendance.objects.filter(section=section, student=enrollment.student.user, status='absent').count()
        
        if total_classes > 0:
            percentage = round((attended / total_classes) * 100, 2)
        else:
            percentage = 0
        
        attendance_data.append({
            'student': enrollment.student,
            'total': total_classes,
            'attended': attended,
            'absent': absent,
            'percentage': percentage
        })
    
    context = {
        'section': section,
        'attendance_data': attendance_data,
    }
    
    return render(request, 'courses/attendance_report.html', context)

@login_required
def announcement_list(request, section_id):
    section = get_object_or_404(ClassSection, id=section_id)
    announcements = Announcement.objects.filter(section=section, is_active=True).order_by('-created_at')
    
    return render(request, 'courses/announcement_list.html', {
        'section': section,
        'announcements': announcements
    })

@login_required
def announcement_create(request, section_id):
    if request.user.role != 'teacher':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    section = get_object_or_404(ClassSection, id=section_id, teacher=request.user)
    
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, request.FILES)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.section = section
            announcement.created_by = request.user
            announcement.save()
            messages.success(request, 'Announcement created successfully!')
            return redirect('course_detail', section_id=section.id)
    else:
        form = AnnouncementForm()
    
    return render(request, 'courses/announcement_form.html', {
        'form': form,
        'section': section,
        'action': 'Create'
    })

@login_required
def announcement_edit(request, pk):
    if request.user.role != 'teacher':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    announcement = get_object_or_404(Announcement, pk=pk, created_by=request.user)
    
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, request.FILES, instance=announcement)
        if form.is_valid():
            form.save()
            messages.success(request, 'Announcement updated successfully!')
            return redirect('course_detail', section_id=announcement.section.id)
    else:
        form = AnnouncementForm(instance=announcement)
    
    return render(request, 'courses/announcement_form.html', {
        'form': form,
        'action': 'Edit'
    })

@login_required
def announcement_delete(request, pk):
    if request.user.role != 'teacher':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    announcement = get_object_or_404(Announcement, pk=pk, created_by=request.user)
    
    if request.method == 'POST':
        section_id = announcement.section.id
        announcement.delete()
        messages.success(request, 'Announcement deleted successfully!')
        return redirect('course_detail', section_id=section_id)
    
    return render(request, 'courses/announcement_confirm_delete.html', {'announcement': announcement})