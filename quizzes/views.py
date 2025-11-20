# quizzes/views.py - COMPLETE IMPLEMENTATION
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Avg, Count
from .models import Quiz, QuizQuestion, QuizOption, QuizAttempt, QuizAnswer, QuizResult
from colleges.models import ClassSection, Enrollment, Student
from .forms import QuizForm, QuizQuestionForm, QuizOptionForm
from django.db import models

@login_required
def quiz_list(request):
    user = request.user
    now = timezone.now()
    
    # Initialize context dictionaries
    context = {}

    if user.role == 'student':
        # --- LOGIC FOR STUDENTS ---
        try:
            # Check for the student profile associated with the user
            student = Student.objects.get(user=user)
        except Student.DoesNotExist:
            # Fallback if student profile is missing
            return render(request, 'quizzes/quiz_list.html', {'available_quizzes': [], 'upcoming_quizzes': []})

        # 1. Get the IDs of all sections the student is enrolled in
        enrolled_section_ids = Enrollment.objects.filter(
            student=student, 
            is_active=True
        ).values_list('section_id', flat=True) # FIX: Uses 'section_id'

        # 2. Filter Quizzes for the student's enrolled sections
        all_quizzes_for_student = Quiz.objects.filter(
            section_id__in=enrolled_section_ids,
            is_active=True
        ).select_related('section', 'section__course').order_by('start_time')

        # 3. Categorize Quizzes by time for students
        context['available_quizzes'] = all_quizzes_for_student.filter(
            start_time__lte=now,
            end_time__gte=now
        )

        context['upcoming_quizzes'] = all_quizzes_for_student.filter(
            start_time__gt=now
        )
        
        # Use the student template
        template_name = 'quizzes/quiz_list.html'

    elif user.role == 'teacher':
        # --- LOGIC FOR TEACHERS ---
        
        # 1. Get all Quizzes created by the logged-in teacher
        teacher_quizzes = Quiz.objects.filter(
            created_by=user
        ).select_related('section', 'section__course').order_by('-start_time')
        
        # 2. Categorize Quizzes for the teacher's management view
        
        # Active: Currently running
        context['active_quizzes'] = teacher_quizzes.filter(
            start_time__lte=now,
            end_time__gte=now,
            is_active=True
        )
        
        # Upcoming: Scheduled for the future
        context['upcoming_quizzes'] = teacher_quizzes.filter(
            start_time__gt=now,
            is_active=True
        )
        
        # Past: Has finished
        context['past_quizzes'] = teacher_quizzes.filter(
            end_time__lt=now
        )
        
        # Use the teacher template
        template_name = 'quizzes/teacher_quiz_list.html'
        
    else:
        # Handle other roles or unassigned users
        return redirect('dashboard') # Or any appropriate fallback page

    return render(request, template_name, context)

@login_required
def quiz_create(request, section_id):
    """Create new quiz"""
    if request.user.role != 'teacher':
        messages.error(request, 'Only teachers can create quizzes.')
        return redirect('dashboard')
    
    section = get_object_or_404(ClassSection, id=section_id, teacher=request.user)
    
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.section = section
            quiz.created_by = request.user
            quiz.save()
            messages.success(request, 'Quiz created successfully! Now add questions.')
            return redirect('add_question', quiz_id=quiz.id)
    else:
        form = QuizForm()
    
    return render(request, 'quizzes/quiz_form.html', {
        'form': form,
        'section': section,
        'action': 'Create'
    })

@login_required
def quiz_detail(request, quiz_id):
    """View quiz details"""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Check access
    if request.user.role == 'student':
        try:
            student = Student.objects.get(user=request.user)
            if not quiz.section.enrollments.filter(student=student, is_active=True).exists():
                messages.error(request, 'You are not enrolled in this course.')
                return redirect('quiz_list')
        except Student.DoesNotExist:
            messages.error(request, 'Student profile not found.')
            return redirect('dashboard')
    elif request.user.role == 'teacher':
        if quiz.section.teacher != request.user:
            messages.error(request, 'Access denied.')
            return redirect('quiz_list')
    
    # Get student's attempts if student
    attempts = None
    can_attempt = False
    
    if request.user.role == 'student':
        student = Student.objects.get(user=request.user)
        attempts = QuizAttempt.objects.filter(quiz=quiz, student=student).order_by('-started_at')
        
        # Check if student can take quiz
        if quiz.is_available():
            if quiz.allow_multiple_attempts:
                attempt_count = attempts.filter(status='submitted').count()
                can_attempt = attempt_count < quiz.max_attempts
            else:
                can_attempt = not attempts.filter(status='submitted').exists()
    
    questions = quiz.questions.all().prefetch_related('options')
    
    context = {
        'quiz': quiz,
        'questions': questions,
        'attempts': attempts,
        'can_attempt': can_attempt,
    }
    
    return render(request, 'quizzes/quiz_detail.html', context)

@login_required
def quiz_edit(request, quiz_id):
    """Edit quiz"""
    if request.user.role != 'teacher':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    quiz = get_object_or_404(Quiz, id=quiz_id, section__teacher=request.user)
    
    if request.method == 'POST':
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            form.save()
            messages.success(request, 'Quiz updated successfully!')
            return redirect('quiz_detail', quiz_id=quiz.id)
    else:
        form = QuizForm(instance=quiz)
    
    return render(request, 'quizzes/quiz_form.html', {
        'form': form,
        'action': 'Edit'
    })

@login_required
def quiz_delete(request, quiz_id):
    """Delete quiz"""
    if request.user.role != 'teacher':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    quiz = get_object_or_404(Quiz, id=quiz_id, section__teacher=request.user)
    
    if request.method == 'POST':
        quiz.delete()
        messages.success(request, 'Quiz deleted successfully!')
        return redirect('quiz_list')
    
    return render(request, 'quizzes/quiz_confirm_delete.html', {'quiz': quiz})

@login_required
def add_question(request, quiz_id):
    """Add question to quiz"""
    if request.user.role != 'teacher':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    quiz = get_object_or_404(Quiz, id=quiz_id, section__teacher=request.user)
    
    # Initialize post_data to be empty for GET requests
    post_data = {} 

    if request.method == 'POST':
        form = QuizQuestionForm(request.POST)
        if form.is_valid():
            # --- Logic to save Question ---
            question = form.save(commit=False)
            question.quiz = quiz
            # Ensure order is set correctly
            question.order = quiz.questions.aggregate(models.Max('order'))['order__max'] or 0 + 1
            question.save()
            
            # --- Logic to save Options ---
            num_options = int(request.POST.get('num_options', 4))
            
            for i in range(num_options):
                option_text = request.POST.get(f'option_{i}')
                is_correct = request.POST.get(f'is_correct_{i}') == 'on'
                
                if option_text:
                    QuizOption.objects.create(
                        question=question,
                        option_text=option_text,
                        is_correct=is_correct,
                        order=i + 1
                    )
            
            messages.success(request, 'Question added successfully!')
            
            # If "Add & Create Another" was clicked
            if request.POST.get('add_another'):
                return redirect('add_question', quiz_id=quiz.id)
            else:
                return redirect('quiz_detail', quiz_id=quiz.id)
        else:
            # If form is invalid, capture the POST data for re-rendering options
            post_data = request.POST
            messages.error(request, 'There were errors in the question form.')
    else:
        form = QuizQuestionForm()
    
    questions = quiz.questions.all().order_by('order')
    
    return render(request, 'quizzes/add_question.html', {
        'form': form,
        'quiz': quiz,
        'questions': questions,
        'post_data': post_data, # Passed back to template for retaining option values
    })

@login_required
def edit_question(request, question_id):
    """Edit quiz question"""
    if request.user.role != 'teacher':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    question = get_object_or_404(QuizQuestion, id=question_id)
    quiz = question.quiz
    
    if quiz.section.teacher != request.user:
        messages.error(request, 'Access denied.')
        return redirect('quiz_list')
    
    if request.method == 'POST':
        form = QuizQuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            
            # Update options
            options = question.options.all()
            for i, option in enumerate(options):
                option_text = request.POST.get(f'option_{i}')
                is_correct = request.POST.get(f'is_correct_{i}') == 'on'
                
                if option_text:
                    option.option_text = option_text
                    option.is_correct = is_correct
                    option.save()
            
            messages.success(request, 'Question updated successfully!')
            return redirect('quiz_detail', quiz_id=quiz.id)
    else:
        form = QuizQuestionForm(instance=question)
    
    return render(request, 'quizzes/edit_question.html', {
        'form': form,
        'question': question,
        'quiz': quiz,
    })

@login_required
def delete_question(request, question_id):
    """Delete quiz question"""
    if request.user.role != 'teacher':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    question = get_object_or_404(QuizQuestion, id=question_id)
    quiz = question.quiz
    
    if quiz.section.teacher != request.user:
        messages.error(request, 'Access denied.')
        return redirect('quiz_list')
    
    if request.method == 'POST':
        question.delete()
        messages.success(request, 'Question deleted successfully!')
        return redirect('quiz_detail', quiz_id=quiz.id)
    
    return render(request, 'quizzes/question_confirm_delete.html', {
        'question': question,
        'quiz': quiz
    })

@login_required
def take_quiz(request, quiz_id):
    """Start taking a quiz"""
    if request.user.role != 'student':
        messages.error(request, 'Only students can take quizzes.')
        return redirect('dashboard')
    
    quiz = get_object_or_404(Quiz, id=quiz_id)
    student = get_object_or_404(Student, user=request.user)
    
    # Check if quiz is available
    if not quiz.is_available():
        messages.error(request, 'This quiz is not currently available.')
        return redirect('quiz_detail', quiz_id=quiz.id)
    
    # Check if student can attempt
    attempts = QuizAttempt.objects.filter(quiz=quiz, student=student)
    
    if not quiz.allow_multiple_attempts and attempts.filter(status='submitted').exists():
        messages.error(request, 'You have already taken this quiz.')
        return redirect('quiz_detail', quiz_id=quiz.id)
    
    if quiz.allow_multiple_attempts:
        attempt_count = attempts.filter(status='submitted').count()
        if attempt_count >= quiz.max_attempts:
            messages.error(request, f'You have reached the maximum number of attempts ({quiz.max_attempts}).')
            return redirect('quiz_detail', quiz_id=quiz.id)
    
    # Check for ongoing attempt
    ongoing_attempt = attempts.filter(status='in_progress').first()
    
    if not ongoing_attempt:
        # Create new attempt
        attempt_number = attempts.count() + 1
        ongoing_attempt = QuizAttempt.objects.create(
            quiz=quiz,
            student=student,
            attempt_number=attempt_number,
            status='in_progress'
        )
    
    # Get questions
    questions = quiz.questions.all().prefetch_related('options')
    if quiz.randomize_questions:
        questions = questions.order_by('?')
    
    context = {
        'quiz': quiz,
        'attempt': ongoing_attempt,
        'questions': questions,
    }
    
    return render(request, 'quizzes/take_quiz.html', context)

@login_required
def submit_quiz(request, attempt_id):
    """Submit quiz answers, calculate score, and create result."""
    if request.user.role != 'student':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, student__user=request.user)
    
    if attempt.status != 'in_progress':
        messages.error(request, 'This attempt has already been submitted.')
        return redirect('quiz_result', attempt_id=attempt.id)
    
    if request.method == 'POST':
        # -----------------------------------------------------------
        # 1. SAVE ANSWERS AND INITIAL GRADE (MCQ/True-False)
        # -----------------------------------------------------------
        for question in attempt.quiz.questions.all():
            answer_key = f'question_{question.id}'
            
            if question.question_type in ['mcq', 'true_false', 'multiple']:
                # Handle single-select (mcq/true_false) and multi-select (multiple)
                selected_options = request.POST.getlist(answer_key) if question.question_type == 'multiple' else [request.POST.get(answer_key)]
                
                # Filter out None/empty strings
                selected_options = [opt for opt in selected_options if opt]

                if selected_options:
                    answer, created = QuizAnswer.objects.get_or_create(
                        attempt=attempt,
                        question=question
                    )
                    # Clear and set selected options
                    answer.selected_options.clear()
                    answer.selected_options.set(selected_options)
                    
                    # Grade the objective question immediately
                    answer.check_answer() 

            elif question.question_type == 'short':
                # Handle Short Answer
                text_answer = request.POST.get(answer_key)
                
                # Note: Short answers are marked incorrect/0 marks initially, requiring manual grading.
                QuizAnswer.objects.update_or_create(
                    attempt=attempt,
                    question=question,
                    defaults={
                        'text_answer': text_answer,
                        'is_correct': False, # Assume incorrect until manually graded
                        'marks_awarded': 0
                    }
                )
        
        # -----------------------------------------------------------
        # 2. FINALIZE ATTEMPT & CALCULATE SCORE
        # -----------------------------------------------------------
        
        # Set final submission status and time
        attempt.status = 'submitted'
        attempt.submitted_at = timezone.now()
        
        # Calculate time taken
        time_taken = (attempt.submitted_at - attempt.started_at).total_seconds() / 60
        attempt.time_taken_minutes = int(time_taken)
        
        # Calculate final score and percentage (updates attempt.score and attempt.percentage in memory)
        attempt.calculate_score()
        
        # *** FIX: Save the updated score, percentage, and submission details to the database ***
        attempt.save() 
        
        # -----------------------------------------------------------
        # 3. CREATE QUIZ RESULT
        # -----------------------------------------------------------
        
        # Find the enrollment object needed for the QuizResult model
        enrollment = Enrollment.objects.filter(
            student=attempt.student,
            section=attempt.quiz.section, # <-- CORRECTED FIELD NAME
        ).first()
        
        # Create result (Check for existence to avoid duplicates on retries/double post)
        if not QuizResult.objects.filter(attempt=attempt).exists():
            QuizResult.objects.create(
                attempt=attempt,
                student=attempt.student,
                enrollment=enrollment, 
                quiz=attempt.quiz,
                score=attempt.score,
                percentage=attempt.percentage,
                passed=attempt.is_passed() 
            )
        
        messages.success(request, 'Quiz submitted successfully!')
        return redirect('quiz_result', attempt_id=attempt.id)
    
    return redirect('take_quiz', quiz_id=attempt.quiz.id)


@login_required
def quiz_result(request, attempt_id):
    """View quiz result"""
    attempt = get_object_or_404(QuizAttempt, id=attempt_id)
    
    # Check access
    if request.user.role == 'student':
        if attempt.student.user != request.user:
            messages.error(request, 'Access denied.')
            return redirect('quiz_list')
    elif request.user.role == 'teacher':
        if attempt.quiz.section.teacher != request.user:
            messages.error(request, 'Access denied.')
            return redirect('quiz_list')
    
    answers = attempt.answers.all().prefetch_related('selected_options', 'question__options')
    
    context = {
        'attempt': attempt,
        'answers': answers,
        'quiz': attempt.quiz,
    }
    
    return render(request, 'quizzes/quiz_result.html', context)

@login_required
def quiz_results(request, quiz_id):
    """View all results for a quiz (teacher only)"""
    if request.user.role != 'teacher':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    quiz = get_object_or_404(Quiz, id=quiz_id, section__teacher=request.user)
    
    # Get all submitted attempts
    attempts = QuizAttempt.objects.filter(
        quiz=quiz,
        status='submitted'
    ).select_related('student__user').order_by('-percentage')
    
    # Calculate statistics
    stats = attempts.aggregate(
        avg_score=Avg('percentage'),
        total_attempts=Count('id'),
        passed_count=Count('id', filter=models.Q(percentage__gte=quiz.passing_marks))
    )
    
    context = {
        'quiz': quiz,
        'attempts': attempts,
        'stats': stats,
    }
    
    return render(request, 'quizzes/quiz_results.html', context)

@login_required
def quiz_analytics(request, quiz_id):
    """Quiz analytics dashboard (teacher only)"""
    if request.user.role != 'teacher':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    quiz = get_object_or_404(Quiz, id=quiz_id, section__teacher=request.user)
    
    # Question-wise analysis
    questions = quiz.questions.all()
    question_stats = []
    
    for question in questions:
        total_answers = QuizAnswer.objects.filter(question=question).count()
        correct_answers = QuizAnswer.objects.filter(question=question, is_correct=True).count()
        
        if total_answers > 0:
            accuracy = (correct_answers / total_answers) * 100
        else:
            accuracy = 0
        
        question_stats.append({
            'question': question,
            'total': total_answers,
            'correct': correct_answers,
            'accuracy': round(accuracy, 2)
        })
    
    context = {
        'quiz': quiz,
        'question_stats': question_stats,
    }
    
    return render(request, 'quizzes/quiz_analytics.html', context)