"""
Automated setup script for Educational Portal Django Project
Run this after creating the project structure

Usage:
    python setup_project.py
"""

import os
import sys
import subprocess
from datetime import datetime, timedelta

def run_command(command, description):
    """Execute a shell command and handle errors"""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e.stderr}")
        return False

def create_demo_data():
    """Create demonstration data for testing"""
    print("\n" + "="*60)
    print("📊 Creating Demo Data")
    print("="*60)
    
    from django.contrib.auth import get_user_model
    from accounts.models import College
    from colleges.models import Department, Course, ClassSection, Teacher, Student, Enrollment
    from courses.models import Assignment, StudyMaterial, Announcement
    from quizzes.models import Quiz, QuizQuestion, QuizOption
    from discussions.models import Badge
    
    User = get_user_model()
    
    # Create College
    college, created = College.objects.get_or_create(
        code='MIT',
        defaults={
            'name': 'Model Institute of Technology',
            'address': '123 Education Street, Knowledge City',
            'established_year': 2000,
            'contact_email': 'info@mit.edu',
            'contact_phone': '+1-234-567-8900'
        }
    )
    print(f"✅ College: {college.name}")
    
    # Create College Admin
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'first_name': 'System',
            'last_name': 'Administrator',
            'email': 'admin@mit.edu',
            'role': 'college_admin',
            'college': college,
            'phone': '+1-234-567-8901'
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
    print(f"✅ Admin: {admin_user.username} (password: admin123)")
    
    # Create Departments
    departments_data = [
        {'name': 'Computer Science', 'code': 'CSE'},
        {'name': 'Electronics & Communication', 'code': 'ECE'},
        {'name': 'Mechanical Engineering', 'code': 'ME'},
    ]
    
    departments = []
    for dept_data in departments_data:
        dept, created = Department.objects.get_or_create(
            college=college,
            code=dept_data['code'],
            defaults={
                'name': dept_data['name'],
                'description': f"{dept_data['name']} Department"
            }
        )
        departments.append(dept)
        print(f"✅ Department: {dept.name}")
    
    # Create Teachers
    teachers_data = [
        {'username': 'teacher1', 'first_name': 'John', 'last_name': 'Smith', 'email': 'john@mit.edu', 'dept': 0, 'emp_id': 'T001'},
        {'username': 'teacher2', 'first_name': 'Sarah', 'last_name': 'Johnson', 'email': 'sarah@mit.edu', 'dept': 0, 'emp_id': 'T002'},
        {'username': 'teacher3', 'first_name': 'Michael', 'last_name': 'Brown', 'email': 'michael@mit.edu', 'dept': 1, 'emp_id': 'T003'},
    ]
    
    teachers = []
    for teacher_data in teachers_data:
        user, created = User.objects.get_or_create(
            username=teacher_data['username'],
            defaults={
                'first_name': teacher_data['first_name'],
                'last_name': teacher_data['last_name'],
                'email': teacher_data['email'],
                'role': 'teacher',
                'college': college,
                'phone': f"+1-234-567-{len(teachers)+8910}"
            }
        )
        if created:
            user.set_password('teacher123')
            user.save()
        
        teacher, created = Teacher.objects.get_or_create(
            user=user,
            defaults={
                'department': departments[teacher_data['dept']],
                'employee_id': teacher_data['emp_id'],
                'qualification': 'Ph.D.',
                'specialization': 'Computer Science',
                'joining_date': datetime.now().date() - timedelta(days=365)
            }
        )
        teachers.append(teacher)
        print(f"✅ Teacher: {user.get_full_name()} ({user.username}/teacher123)")
    
    # Create Courses
    courses_data = [
        {'name': 'Data Structures & Algorithms', 'code': 'CS101', 'dept': 0, 'credits': 4, 'sem': 3},
        {'name': 'Database Management Systems', 'code': 'CS201', 'dept': 0, 'credits': 4, 'sem': 4},
        {'name': 'Web Development', 'code': 'CS301', 'dept': 0, 'credits': 3, 'sem': 5},
        {'name': 'Digital Electronics', 'code': 'EC101', 'dept': 1, 'credits': 4, 'sem': 3},
    ]
    
    courses = []
    for course_data in courses_data:
        course, created = Course.objects.get_or_create(
            department=departments[course_data['dept']],
            code=course_data['code'],
            defaults={
                'name': course_data['name'],
                'description': f"Comprehensive course on {course_data['name']}",
                'credits': course_data['credits'],
                'semester': course_data['sem']
            }
        )
        courses.append(course)
        print(f"✅ Course: {course.name}")
    
    # Create Class Sections
    sections = []
    for i, course in enumerate(courses[:3]):  # Create sections for first 3 courses
        section, created = ClassSection.objects.get_or_create(
            course=course,
            section_name='A',
            academic_year='2024-2025',
            defaults={
                'year': 2,
                'teacher': teachers[i % len(teachers)].user,
                'max_students': 60
            }
        )
        sections.append(section)
        print(f"✅ Section: {section}")
    
    # Create Students
    students_data = [
        {'username': 'student1', 'first_name': 'Alice', 'last_name': 'Williams', 'roll': 'S2024001', 'dept': 0},
        {'username': 'student2', 'first_name': 'Bob', 'last_name': 'Davis', 'roll': 'S2024002', 'dept': 0},
        {'username': 'student3', 'first_name': 'Charlie', 'last_name': 'Miller', 'roll': 'S2024003', 'dept': 0},
        {'username': 'student4', 'first_name': 'Diana', 'last_name': 'Wilson', 'roll': 'S2024004', 'dept': 0},
        {'username': 'student5', 'first_name': 'Emma', 'last_name': 'Moore', 'roll': 'S2024005', 'dept': 1},
    ]
    
    students = []
    for student_data in students_data:
        user, created = User.objects.get_or_create(
            username=student_data['username'],
            defaults={
                'first_name': student_data['first_name'],
                'last_name': student_data['last_name'],
                'email': f"{student_data['username']}@mit.edu",
                'role': 'student',
                'college': college,
                'phone': f"+1-234-567-{len(students)+8920}"
            }
        )
        if created:
            user.set_password('student123')
            user.save()
        
        student, created = Student.objects.get_or_create(
            user=user,
            defaults={
                'department': departments[student_data['dept']],
                'roll_number': student_data['roll'],
                'admission_year': 2024,
                'current_semester': 3,
                'guardian_name': f"Parent of {user.first_name}",
                'guardian_phone': f"+1-234-567-{len(students)+9000}"
            }
        )
        students.append(student)
        print(f"✅ Student: {user.get_full_name()} ({user.username}/student123)")
    
    # Enroll students in sections
    for student in students[:4]:  # Enroll first 4 students in CSE courses
        for section in sections[:2]:
            Enrollment.objects.get_or_create(
                student=student,
                section=section,
                defaults={'is_active': True}
            )
    print(f"✅ Enrolled students in courses")
    
    # Create Study Materials
    for section in sections:
        StudyMaterial.objects.get_or_create(
            section=section,
            title=f"Introduction to {section.course.name}",
            defaults={
                'description': 'Introductory lecture slides',
                'material_type': 'slides',
                'external_link': 'https://example.com/slides',
                'uploaded_by': section.teacher,
                'is_active': True
            }
        )
    print(f"✅ Created study materials")
    
    # Create Assignments
    for section in sections:
        Assignment.objects.get_or_create(
            section=section,
            title=f"Assignment 1 - {section.course.code}",
            defaults={
                'description': f"First assignment for {section.course.name}",
                'total_marks': 100,
                'due_date': datetime.now() + timedelta(days=7),
                'created_by': section.teacher,
                'status': 'published',
                'allow_late_submission': True
            }
        )
    print(f"✅ Created assignments")
    
    # Create Quiz
    quiz, created = Quiz.objects.get_or_create(
        section=sections[0],
        title='Mid-term Quiz - Data Structures',
        defaults={
            'description': 'Mid-term assessment on arrays and linked lists',
            'duration_minutes': 30,
            'total_marks': 50,
            'passing_marks': 25,
            'difficulty': 'medium',
            'start_time': datetime.now(),
            'end_time': datetime.now() + timedelta(days=7),
            'is_active': True,
            'allow_multiple_attempts': False,
            'show_results_immediately': True,
            'created_by': sections[0].teacher
        }
    )
    
    if created:
        # Add quiz questions
        q1 = QuizQuestion.objects.create(
            quiz=quiz,
            question_text='What is the time complexity of accessing an element in an array?',
            question_type='mcq',
            marks=5,
            order=1
        )
        QuizOption.objects.create(question=q1, option_text='O(1)', is_correct=True, order=1)
        QuizOption.objects.create(question=q1, option_text='O(n)', is_correct=False, order=2)
        QuizOption.objects.create(question=q1, option_text='O(log n)', is_correct=False, order=3)
        QuizOption.objects.create(question=q1, option_text='O(n²)', is_correct=False, order=4)
        
        q2 = QuizQuestion.objects.create(
            quiz=quiz,
            question_text='Which data structure follows LIFO principle?',
            question_type='mcq',
            marks=5,
            order=2
        )
        QuizOption.objects.create(question=q2, option_text='Queue', is_correct=False, order=1)
        QuizOption.objects.create(question=q2, option_text='Stack', is_correct=True, order=2)
        QuizOption.objects.create(question=q2, option_text='Array', is_correct=False, order=3)
        QuizOption.objects.create(question=q2, option_text='Tree', is_correct=False, order=4)
        
        print(f"✅ Created quiz with questions")
    
    # Create Badges
    badges_data = [
        {'name': 'First Steps', 'type': 'participation', 'desc': 'Complete your first assignment', 'points': 10},
        {'name': 'Quiz Master', 'type': 'achievement', 'desc': 'Score 100% in a quiz', 'points': 50},
        {'name': 'Perfect Attendance', 'type': 'consistency', 'desc': 'Maintain 100% attendance', 'points': 30},
        {'name': 'Discussion Champion', 'type': 'participation', 'desc': 'Post 10 forum discussions', 'points': 20},
    ]
    
    for badge_data in badges_data:
        Badge.objects.get_or_create(
            name=badge_data['name'],
            defaults={
                'description': badge_data['desc'],
                'badge_type': badge_data['type'],
                'criteria': {},
                'points': badge_data['points'],
                'is_active': True
            }
        )
    print(f"✅ Created badges")
    
    # Create Announcements
    for section in sections:
        Announcement.objects.get_or_create(
            section=section,
            title=f"Welcome to {section.course.name}!",
            defaults={
                'content': f"Welcome to the course! Please check the course materials and upcoming assignments.",
                'priority': 'high',
                'created_by': section.teacher,
                'is_active': True
            }
        )
    print(f"✅ Created announcements")
    
    print("\n" + "="*60)
    print("✨ Demo data creation completed!")
    print("="*60)
    print("\n📝 Test Credentials:")
    print("-" * 60)
    print("Admin:    username='admin'    password='admin123'")
    print("Teacher:  username='teacher1' password='teacher123'")
    print("Student:  username='student1' password='student123'")
    print("-" * 60)

def main():
    print("="*60)
    print("🎓 Educational Portal - Setup Script")
    print("="*60)
    
    # Check if Django is available
    try:
        import django
        print(f"✅ Django {django.get_version()} detected")
    except ImportError:
        print("❌ Django not found. Please install requirements first:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    
    # Setup Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'educational_portal.settings')
    django.setup()
    
    # Run migrations
    if not run_command('python manage.py makemigrations', 'Creating migrations'):
        print("⚠️  Migration creation failed, but continuing...")
    
    if not run_command('python manage.py migrate', 'Applying migrations'):
        print("❌ Migration failed. Please check your database configuration.")
        sys.exit(1)
    
    # Create demo data
    try:
        create_demo_data()
    except Exception as e:
        print(f"❌ Error creating demo data: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Collect static files
    print("\n💡 Tip: Run 'python manage.py collectstatic' before deploying to production")
    
    print("\n" + "="*60)
    print("🎉 Setup completed successfully!")
    print("="*60)
    print("\nNext steps:")
    print("1. Start the development server:")
    print("   python manage.py runserver")
    print("\n2. Open your browser and navigate to:")
    print("   http://127.0.0.1:8000/")
    print("\n3. Login with the credentials above")
    print("="*60)

if __name__ == '__main__':
    main()