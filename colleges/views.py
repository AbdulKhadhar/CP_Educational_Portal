# colleges/views.py - COMPLETE IMPLEMENTATION
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth import get_user_model
from .models import Department, Course, ClassSection, Teacher, Student, Enrollment
from .forms import (DepartmentForm, CourseForm, ClassSectionForm, 
                   TeacherForm, StudentForm, EnrollmentForm)

User = get_user_model()

# ============= DEPARTMENT VIEWS =============

@login_required
def department_list(request):
    """List all departments"""
    if request.user.role != 'college_admin':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    college = request.user.college
    departments = Department.objects.filter(college=college).select_related('hod')
    
    # Search functionality
    search = request.GET.get('search', '')
    if search:
        departments = departments.filter(
            Q(name__icontains=search) | Q(code__icontains=search)
        )
    
    context = {
        'departments': departments,
        'search': search,
    }
    return render(request, 'colleges/department_list.html', context)

@login_required
def department_create(request):
    """Create new department"""
    if request.user.role != 'college_admin':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            department = form.save(commit=False)
            department.college = request.user.college
            department.save()
            messages.success(request, f'Department "{department.name}" created successfully!')
            return redirect('department_list')
    else:
        form = DepartmentForm()
    
    return render(request, 'colleges/department_form.html', {'form': form, 'action': 'Create'})

@login_required
def department_edit(request, pk):
    """Edit department"""
    if request.user.role != 'college_admin':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    department = get_object_or_404(Department, pk=pk, college=request.user.college)
    
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            messages.success(request, 'Department updated successfully!')
            return redirect('department_list')
    else:
        form = DepartmentForm(instance=department)
    
    return render(request, 'colleges/department_form.html', {'form': form, 'action': 'Edit'})

@login_required
def department_delete(request, pk):
    """Delete department"""
    if request.user.role != 'college_admin':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    department = get_object_or_404(Department, pk=pk, college=request.user.college)
    
    if request.method == 'POST':
        name = department.name
        department.delete()
        messages.success(request, f'Department "{name}" deleted successfully!')
        return redirect('department_list')
    
    return render(request, 'colleges/department_confirm_delete.html', {'department': department})

# ============= COURSE VIEWS =============

@login_required
def course_list(request):
    """List all courses"""
    if request.user.role != 'college_admin':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    college = request.user.college
    courses = Course.objects.filter(
        department__college=college
    ).select_related('department')
    
    # Filter by department
    dept_id = request.GET.get('department')
    if dept_id:
        courses = courses.filter(department_id=dept_id)
    
    departments = Department.objects.filter(college=college)
    
    context = {
        'courses': courses,
        'departments': departments,
        'selected_dept': dept_id,
    }
    return render(request, 'colleges/course_list.html', context)

@login_required
def course_create(request, dept_id):
    """Create new course"""
    if request.user.role != 'college_admin':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    department = get_object_or_404(Department, pk=dept_id, college=request.user.college)
    
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.department = department
            course.save()
            messages.success(request, f'Course "{course.name}" created successfully!')
            return redirect('course_list')
    else:
        form = CourseForm()
    
    return render(request, 'colleges/course_form.html', {
        'form': form, 
        'department': department,
        'action': 'Create'
    })

@login_required
def course_edit(request, pk):
    """Edit course"""
    if request.user.role != 'college_admin':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    course = get_object_or_404(
        Course, pk=pk, department__college=request.user.college
    )
    
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course updated successfully!')
            return redirect('course_list')
    else:
        form = CourseForm(instance=course)
    
    return render(request, 'colleges/course_form.html', {
        'form': form,
        'action': 'Edit'
    })

@login_required
def course_delete(request, pk):
    """Delete course"""
    if request.user.role != 'college_admin':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    course = get_object_or_404(
        Course, pk=pk, department__college=request.user.college
    )
    
    if request.method == 'POST':
        name = course.name
        course.delete()
        messages.success(request, f'Course "{name}" deleted successfully!')
        return redirect('course_list')
    
    return render(request, 'colleges/course_confirm_delete.html', {'course': course})

# ============= SECTION VIEWS =============

@login_required
def section_list(request):
    """List all sections"""
    college = request.user.college
    
    if request.user.role == 'college_admin':
        sections = ClassSection.objects.filter(
            course__department__college=college
        ).select_related('course', 'teacher')
    elif request.user.role == 'teacher':
        sections = ClassSection.objects.filter(teacher=request.user)
    else:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    context = {'sections': sections}
    return render(request, 'colleges/section_list.html', context)

@login_required
def section_create(request, course_id):
    """Create new section"""
    if request.user.role != 'college_admin':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    course = get_object_or_404(
        Course, pk=course_id, department__college=request.user.college
    )
    
    if request.method == 'POST':
        form = ClassSectionForm(request.POST)
        if form.is_valid():
            section = form.save(commit=False)
            section.course = course
            section.save()
            messages.success(request, 'Section created successfully!')
            return redirect('section_list')
    else:
        form = ClassSectionForm()
    
    return render(request, 'colleges/section_form.html', {
        'form': form,
        'course': course,
        'action': 'Create'
    })

@login_required
def section_edit(request, pk):
    """Edit section"""
    if request.user.role != 'college_admin':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    section = get_object_or_404(
        ClassSection, pk=pk, course__department__college=request.user.college
    )
    
    if request.method == 'POST':
        form = ClassSectionForm(request.POST, instance=section)
        if form.is_valid():
            form.save()
            messages.success(request, 'Section updated successfully!')
            return redirect('section_list')
    else:
        form = ClassSectionForm(instance=section)
    
    return render(request, 'colleges/section_form.html', {
        'form': form,
        'action': 'Edit'
    })

@login_required
def section_delete(request, pk):
    """Delete section"""
    if request.user.role != 'college_admin':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    section = get_object_or_404(
        ClassSection, pk=pk, course__department__college=request.user.college
    )
    
    if request.method == 'POST':
        section.delete()
        messages.success(request, 'Section deleted successfully!')
        return redirect('section_list')
    
    return render(request, 'colleges/section_confirm_delete.html', {'section': section})

# ============= TEACHER VIEWS =============

@login_required
def teacher_list(request):
    """List all teachers"""
    if request.user.role != 'college_admin':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    college = request.user.college
    teachers = Teacher.objects.filter(
        department__college=college
    ).select_related('user', 'department')
    
    context = {'teachers': teachers}
    return render(request, 'colleges/teacher_list.html', context)

@login_required
def teacher_register(request):
    """Register new teacher"""
    
    if request.user.role != 'college_admin':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    college_departments_queryset = Department.objects.filter(college=request.user.college)
    
    if request.method == 'POST':
        form = TeacherForm(request.POST)
        form.fields['department'].queryset = college_departments_queryset
        if form.is_valid():
            # Create user first
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                role='teacher',
                college=request.user.college,
                phone=form.cleaned_data['phone']
            )
            
            # Create teacher profile
            teacher = form.save(commit=False)
            teacher.user = user
            
            teacher.save()
            
            messages.success(request, f'Teacher "{user.get_full_name()}" registered successfully!')
            return redirect('teacher_list')
    else:
        form = TeacherForm()
       
        form.fields['department'].queryset = college_departments_queryset
    
   
    return render(request, 'colleges/teacher_form.html', {
        'form': form,
        'action': 'Register'
    })

@login_required
def teacher_edit(request, pk):
    """Edit teacher details"""
    if request.user.role != 'college_admin':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    teacher = get_object_or_404(
        Teacher, pk=pk, department__college=request.user.college
    )
    
    if request.method == 'POST':
        # Update user details
        teacher.user.first_name = request.POST.get('first_name')
        teacher.user.last_name = request.POST.get('last_name')
        teacher.user.email = request.POST.get('email')
        teacher.user.phone = request.POST.get('phone')
        teacher.user.save()
        
        # Update teacher details
        teacher.qualification = request.POST.get('qualification')
        teacher.specialization = request.POST.get('specialization')
        teacher.save()
        
        messages.success(request, 'Teacher updated successfully!')
        return redirect('teacher_list')
    
    return render(request, 'colleges/teacher_edit.html', {'teacher': teacher})

@login_required
def teacher_delete(request, pk):
    """Delete teacher"""
    if request.user.role != 'college_admin':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    teacher = get_object_or_404(
        Teacher, pk=pk, department__college=request.user.college
    )
    
    if request.method == 'POST':
        name = teacher.user.get_full_name()
        user = teacher.user
        teacher.delete()
        user.delete()
        messages.success(request, f'Teacher "{name}" deleted successfully!')
        return redirect('teacher_list')
    
    return render(request, 'colleges/teacher_confirm_delete.html', {'teacher': teacher})

# ============= STUDENT VIEWS =============

@login_required
def student_list(request):
    """List all students"""
    if request.user.role != 'college_admin':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    college = request.user.college
    students = Student.objects.filter(
        department__college=college
    ).select_related('user', 'department')
    
    # Search functionality
    search = request.GET.get('search', '')
    if search:
        students = students.filter(
            Q(roll_number__icontains=search) |
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search)
        )
    
    context = {
        'students': students,
        'search': search,
    }
    return render(request, 'colleges/student_list.html', context)

@login_required
def bulk_enroll_existing_students(request):
    """
    Finds existing students and enrolls them into all relevant sections 
    based on their department and current semester.
    (This is designed to be run manually by the college admin to fix missing enrollment data.)
    """
    if request.user.role != 'college_admin':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        # Filter students and sections by the college of the admin
        college = request.user.college
        
        # 1. Get all students that belong to the college
        students = Student.objects.filter(
            department__college=college,
            user__is_active=True
            ).select_related('department')

        total_new_enrollments = 0
        
        for student in students:
            # 2. Find all ClassSections that match the student's current department and semester
            relevant_sections = ClassSection.objects.filter(
                course__department=student.department,
                course__semester=student.current_semester
            )
            
            # 3. Prepare enrollment records for bulk creation
            # Use a list comprehension to build the list of new Enrollment objects
            new_enrollments = [
                Enrollment(student=student, section=section)
                for section in relevant_sections
            ]
            
            # 4. Bulk create them, ignoring existing 'unique_together' violations
            created_enrollments = Enrollment.objects.bulk_create(new_enrollments, ignore_conflicts=True)
            total_new_enrollments += len(created_enrollments)

        messages.success(request, f'Bulk enrollment complete. Created {total_new_enrollments} new enrollment records for students in your college.')
        return redirect('student_list') # Redirect to student list or dashboard
    
    # Render a confirmation page
    return render(request, 'colleges/bulk_enroll_confirm.html', {})


@login_required
def student_register(request):
    """Register new student AND automatically enroll them in appropriate sections"""
    if request.user.role != 'college_admin':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    college_departments_queryset = Department.objects.filter(college=request.user.college)

    if request.method == 'POST':
        form = StudentForm(request.POST)
        form.fields['department'].queryset = college_departments_queryset # Apply queryset for security/context
        
        if form.is_valid():
            # 1. Create User
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                role='student',
                college=request.user.college,
                phone=form.cleaned_data['phone']
            )
            
            # 2. Create Student Profile
            student = form.save(commit=False)
            student.user = user
            # Department and Semester are cleaned_data from the form
            student.department = form.cleaned_data['department']
            student.current_semester = form.cleaned_data['current_semester']
            student.save()
            
            # 3. --- NEW: AUTO-ENROLLMENT LOGIC ---
            
            # Find all active sections for this student's department and current semester
            relevant_sections = ClassSection.objects.filter(
                course__department=student.department,
                course__semester=student.current_semester # Assumes Course model has a 'semester' field
            )
            
            new_enrollments = []
            for section in relevant_sections:
                new_enrollments.append(
                    Enrollment(student=student, section=section)
                )

            # Bulk create all new enrollments at once
            Enrollment.objects.bulk_create(new_enrollments, ignore_conflicts=True)

            # --- END AUTO-ENROLLMENT LOGIC ---
            
            messages.success(request, f'Student "{user.get_full_name()}" registered and enrolled in {len(new_enrollments)} courses successfully!')
            return redirect('student_list')
    else:
        form = StudentForm()
    
    # Ensure the department dropdown only shows departments from the current college
    form.fields['department'].queryset = college_departments_queryset
    
    return render(request, 'colleges/student_form.html', {
        'form': form,
        'action': 'Register'
    })

@login_required
def student_edit(request, pk):
    """Edit student details"""
    if request.user.role != 'college_admin':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    student = get_object_or_404(
        Student, pk=pk, department__college=request.user.college
    )
    
    if request.method == 'POST':
        # Update user details
        student.user.first_name = request.POST.get('first_name')
        student.user.last_name = request.POST.get('last_name')
        student.user.email = request.POST.get('email')
        student.user.phone = request.POST.get('phone')
        student.user.save()
        
        # Update student details
        student.current_semester = request.POST.get('current_semester')
        student.guardian_name = request.POST.get('guardian_name')
        student.guardian_phone = request.POST.get('guardian_phone')
        student.save()
        
        messages.success(request, 'Student updated successfully!')
        return redirect('student_list')
    
    return render(request, 'colleges/student_edit.html', {'student': student})

@login_required
def student_delete(request, pk):
    """Delete student"""
    if request.user.role != 'college_admin':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    student = get_object_or_404(
        Student, pk=pk, department__college=request.user.college
    )
    
    if request.method == 'POST':
        name = student.user.get_full_name()
        user = student.user
        student.delete()
        user.delete()
        messages.success(request, f'Student "{name}" deleted successfully!')
        return redirect('student_list')
    
    return render(request, 'colleges/student_confirm_delete.html', {'student': student})

@login_required
def student_details(request, pk):
    """View student details and performance"""
    student = get_object_or_404(Student, pk=pk)
    
    # Check access
    if request.user.role == 'student':
        if student.user != request.user:
            messages.error(request, 'Access denied.')
            return redirect('dashboard')
    elif request.user.role not in ['college_admin', 'teacher']:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    # Get enrollments
    enrollments = Enrollment.objects.filter(
        student=student, is_active=True
    ).select_related('section__course')
    
    # Calculate SPI
    spi = student.calculate_spi()
    
    # Get recent submissions
    from courses.models import Submission
    submissions = Submission.objects.filter(
        student=student
    ).select_related('assignment')[:5]
    
    # Get quiz results
    from quizzes.models import QuizResult
    quiz_results = QuizResult.objects.filter(
        student=student
    ).select_related('quiz')[:5]
    
    context = {
        'student': student,
        'enrollments': enrollments,
        'spi': spi,
        'submissions': submissions,
        'quiz_results': quiz_results,
    }
    
    return render(request, 'colleges/student_details.html', context)

# ============= ENROLLMENT VIEWS =============

@login_required
def enrollment_list(request):
    """List all enrollments"""
    if request.user.role != 'college_admin':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    college = request.user.college
    enrollments = Enrollment.objects.filter(
        section__course__department__college=college
    ).select_related('student__user', 'section__course')
    
    context = {'enrollments': enrollments}
    return render(request, 'colleges/enrollment_list.html', context)

@login_required
def enrollment_create(request):
    """Create new enrollment"""
    if request.user.role != 'college_admin':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            enrollment = form.save()
            messages.success(request, 'Student enrolled successfully!')
            return redirect('enrollment_list')
    else:
        form = EnrollmentForm()
    
    college = request.user.college
    students = Student.objects.filter(department__college=college)
    sections = ClassSection.objects.filter(course__department__college=college)
    
    return render(request, 'colleges/enrollment_form.html', {
        'form': form,
        'students': students,
        'sections': sections,
    })

@login_required
def enrollment_delete(request, pk):
    """Delete enrollment"""
    if request.user.role != 'college_admin':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    enrollment = get_object_or_404(Enrollment, pk=pk)
    
    if request.method == 'POST':
        enrollment.is_active = False
        enrollment.save()
        messages.success(request, 'Enrollment deactivated successfully!')
        return redirect('enrollment_list')
    
    return render(request, 'colleges/enrollment_confirm_delete.html', {'enrollment': enrollment})