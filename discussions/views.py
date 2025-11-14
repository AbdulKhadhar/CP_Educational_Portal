# discussions/views.py - COMPLETE IMPLEMENTATION
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse
from colleges.models import ClassSection, Student, Enrollment
from .models import Discussion, Comment, CommentVote
from .forms import DiscussionForm, CommentForm

@login_required
def discussion_list(request, section_id):
    """List all discussions for a section"""
    section = get_object_or_404(ClassSection, id=section_id)
    
    # Check access
    if request.user.role == 'student':
        try:
            student = Student.objects.get(user=request.user)
            if not Enrollment.objects.filter(student=student, section=section, is_active=True).exists():
                messages.error(request, 'You are not enrolled in this course.')
                return redirect('dashboard')
        except Student.DoesNotExist:
            messages.error(request, 'Student profile not found.')
            return redirect('dashboard')
    elif request.user.role == 'teacher':
        if section.teacher != request.user:
            messages.error(request, 'Access denied.')
            return redirect('dashboard')
    
    # Get discussions
    discussions = Discussion.objects.filter(section=section).select_related('author')
    
    # Filter by category
    category = request.GET.get('category')
    if category:
        discussions = discussions.filter(category=category)
    
    # Search
    search = request.GET.get('search')
    if search:
        discussions = discussions.filter(
            Q(title__icontains=search) | Q(content__icontains=search)
        )
    
    # Annotate with comment count
    discussions = discussions.annotate(comment_count=Count('comments'))
    
    context = {
        'section': section,
        'discussions': discussions,
        'category': category,
        'search': search,
    }
    
    return render(request, 'discussions/discussion_list.html', context)

@login_required
def discussion_create(request, section_id):
    """Create new discussion"""
    section = get_object_or_404(ClassSection, id=section_id)
    
    # Check access
    if request.user.role == 'student':
        try:
            student = Student.objects.get(user=request.user)
            if not Enrollment.objects.filter(student=student, section=section, is_active=True).exists():
                messages.error(request, 'You are not enrolled in this course.')
                return redirect('dashboard')
        except Student.DoesNotExist:
            messages.error(request, 'Student profile not found.')
            return redirect('dashboard')
    elif request.user.role == 'teacher':
        if section.teacher != request.user:
            messages.error(request, 'Access denied.')
            return redirect('dashboard')
    
    if request.method == 'POST':
        form = DiscussionForm(request.POST, request.FILES)
        if form.is_valid():
            discussion = form.save(commit=False)
            discussion.section = section
            discussion.author = request.user
            discussion.save()
            messages.success(request, 'Discussion created successfully!')
            return redirect('discussion_detail', pk=discussion.id)
    else:
        form = DiscussionForm()
    
    return render(request, 'discussions/discussion_form.html', {
        'form': form,
        'section': section,
        'action': 'Create'
    })

@login_required
def discussion_detail(request, pk):
    """View discussion details and comments"""
    discussion = get_object_or_404(Discussion, pk=pk)
    
    # Increment view count
    discussion.views_count += 1
    discussion.save(update_fields=['views_count'])
    
    # Check access
    if request.user.role == 'student':
        try:
            student = Student.objects.get(user=request.user)
            if not Enrollment.objects.filter(student=student, section=discussion.section, is_active=True).exists():
                messages.error(request, 'You are not enrolled in this course.')
                return redirect('dashboard')
        except Student.DoesNotExist:
            messages.error(request, 'Student profile not found.')
            return redirect('dashboard')
    elif request.user.role == 'teacher':
        if discussion.section.teacher != request.user:
            messages.error(request, 'Access denied.')
            return redirect('dashboard')
    
    # Get comments (top-level only, replies will be nested)
    comments = discussion.comments.filter(parent=None).select_related('author').prefetch_related('replies')
    
    context = {
        'discussion': discussion,
        'comments': comments,
        'can_moderate': request.user == discussion.section.teacher or request.user.role == 'college_admin',
    }
    
    return render(request, 'discussions/discussion_detail.html', context)

@login_required
def discussion_edit(request, pk):
    """Edit discussion"""
    discussion = get_object_or_404(Discussion, pk=pk, author=request.user)
    
    if request.method == 'POST':
        form = DiscussionForm(request.POST, request.FILES, instance=discussion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Discussion updated successfully!')
            return redirect('discussion_detail', pk=discussion.id)
    else:
        form = DiscussionForm(instance=discussion)
    
    return render(request, 'discussions/discussion_form.html', {
        'form': form,
        'action': 'Edit'
    })

@login_required
def discussion_delete(request, pk):
    """Delete discussion"""
    discussion = get_object_or_404(Discussion, pk=pk)
    
    # Check permission
    if discussion.author != request.user and request.user != discussion.section.teacher:
        messages.error(request, 'Access denied.')
        return redirect('discussion_detail', pk=pk)
    
    if request.method == 'POST':
        section_id = discussion.section.id
        discussion.delete()
        messages.success(request, 'Discussion deleted successfully!')
        return redirect('discussion_list', section_id=section_id)
    
    return render(request, 'discussions/discussion_confirm_delete.html', {'discussion': discussion})

@login_required
def discussion_toggle_pin(request, pk):
    """Pin/unpin discussion (teacher only)"""
    discussion = get_object_or_404(Discussion, pk=pk)
    
    if request.user != discussion.section.teacher and request.user.role != 'college_admin':
        messages.error(request, 'Access denied.')
        return redirect('discussion_detail', pk=pk)
    
    discussion.is_pinned = not discussion.is_pinned
    discussion.save()
    
    status = 'pinned' if discussion.is_pinned else 'unpinned'
    messages.success(request, f'Discussion {status} successfully!')
    
    return redirect('discussion_detail', pk=pk)

@login_required
def discussion_toggle_lock(request, pk):
    """Lock/unlock discussion (teacher only)"""
    discussion = get_object_or_404(Discussion, pk=pk)
    
    if request.user != discussion.section.teacher and request.user.role != 'college_admin':
        messages.error(request, 'Access denied.')
        return redirect('discussion_detail', pk=pk)
    
    discussion.is_locked = not discussion.is_locked
    discussion.save()
    
    status = 'locked' if discussion.is_locked else 'unlocked'
    messages.success(request, f'Discussion {status} successfully!')
    
    return redirect('discussion_detail', pk=pk)

@login_required
def discussion_resolve(request, pk):
    """Mark discussion as resolved"""
    discussion = get_object_or_404(Discussion, pk=pk)
    
    # Only author or teacher can resolve
    if request.user != discussion.author and request.user != discussion.section.teacher:
        messages.error(request, 'Access denied.')
        return redirect('discussion_detail', pk=pk)
    
    discussion.is_resolved = not discussion.is_resolved
    discussion.save()
    
    status = 'marked as resolved' if discussion.is_resolved else 'reopened'
    messages.success(request, f'Discussion {status}!')
    
    return redirect('discussion_detail', pk=pk)

@login_required
def add_comment(request, discussion_id):
    """Add comment to discussion"""
    discussion = get_object_or_404(Discussion, pk=discussion_id)
    
    if discussion.is_locked and request.user != discussion.section.teacher:
        messages.error(request, 'This discussion is locked.')
        return redirect('discussion_detail', pk=discussion_id)
    
    # Check access
    if request.user.role == 'student':
        try:
            student = Student.objects.get(user=request.user)
            if not Enrollment.objects.filter(student=student, section=discussion.section, is_active=True).exists():
                messages.error(request, 'You are not enrolled in this course.')
                return redirect('dashboard')
        except Student.DoesNotExist:
            messages.error(request, 'Student profile not found.')
            return redirect('dashboard')
    
    if request.method == 'POST':
        form = CommentForm(request.POST, request.FILES)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.discussion = discussion
            comment.author = request.user
            
            # Check if it's a reply
            parent_id = request.POST.get('parent_id')
            if parent_id:
                parent_comment = get_object_or_404(Comment, pk=parent_id)
                comment.parent = parent_comment
            
            comment.save()
            messages.success(request, 'Comment added successfully!')
            return redirect('discussion_detail', pk=discussion_id)
    else:
        form = CommentForm()
    
    return render(request, 'discussions/add_comment.html', {
        'form': form,
        'discussion': discussion
    })

@login_required
def edit_comment(request, comment_id):
    """Edit comment"""
    comment = get_object_or_404(Comment, pk=comment_id, author=request.user)
    
    if request.method == 'POST':
        form = CommentForm(request.POST, request.FILES, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Comment updated successfully!')
            return redirect('discussion_detail', pk=comment.discussion.id)
    else:
        form = CommentForm(instance=comment)
    
    return render(request, 'discussions/edit_comment.html', {
        'form': form,
        'comment': comment
    })

@login_required
def delete_comment(request, comment_id):
    """Delete comment"""
    comment = get_object_or_404(Comment, pk=comment_id)
    
    # Check permission
    if comment.author != request.user and request.user != comment.discussion.section.teacher:
        messages.error(request, 'Access denied.')
        return redirect('discussion_detail', pk=comment.discussion.id)
    
    if request.method == 'POST':
        discussion_id = comment.discussion.id
        comment.delete()
        messages.success(request, 'Comment deleted successfully!')
        return redirect('discussion_detail', pk=discussion_id)
    
    return render(request, 'discussions/comment_confirm_delete.html', {'comment': comment})

@login_required
def vote_comment(request, comment_id):
    """Vote on a comment"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
    comment = get_object_or_404(Comment, pk=comment_id)
    vote_type = int(request.POST.get('vote_type', 1))  # 1 for upvote, -1 for downvote
    
    # Check if user already voted
    existing_vote = CommentVote.objects.filter(comment=comment, user=request.user).first()
    
    if existing_vote:
        if existing_vote.vote_type == vote_type:
            # Remove vote
            existing_vote.delete()
            comment.upvotes -= vote_type
            action = 'removed'
        else:
            # Change vote
            existing_vote.vote_type = vote_type
            existing_vote.save()
            comment.upvotes += (2 * vote_type)  # Change from -1 to 1 or vice versa
            action = 'changed'
    else:
        # New vote
        CommentVote.objects.create(comment=comment, user=request.user, vote_type=vote_type)
        comment.upvotes += vote_type
        action = 'added'
    
    comment.save()
    
    return JsonResponse({
        'success': True,
        'action': action,
        'upvotes': comment.upvotes
    })

@login_required
def mark_solution(request, comment_id):
    """Mark comment as solution (teacher only)"""
    comment = get_object_or_404(Comment, pk=comment_id)
    
    # Only teacher or discussion author can mark solution
    if request.user != comment.discussion.section.teacher and request.user != comment.discussion.author:
        messages.error(request, 'Access denied.')
        return redirect('discussion_detail', pk=comment.discussion.id)
    
    # Unmark other solutions in this discussion
    Comment.objects.filter(discussion=comment.discussion, is_solution=True).update(is_solution=False)
    
    # Mark this as solution
    comment.is_solution = not comment.is_solution
    comment.save()
    
    if comment.is_solution:
        messages.success(request, 'Comment marked as solution!')
    else:
        messages.success(request, 'Solution mark removed!')
    
    return redirect('discussion_detail', pk=comment.discussion.id)