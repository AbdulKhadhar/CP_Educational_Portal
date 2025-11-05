# discussions/admin.py
from django.contrib import admin
from .models import Discussion, Comment, CommentVote, Badge, StudentBadge, Certificate, PeerGroup, GroupActivity

@admin.register(Discussion)
class DiscussionAdmin(admin.ModelAdmin):
    list_display = ['title', 'section', 'author', 'category', 'is_pinned', 'is_locked', 'is_resolved', 'views_count', 'created_at']
    list_filter = ['category', 'is_pinned', 'is_locked', 'is_resolved', 'created_at']
    search_fields = ['title', 'content', 'author__username']
    raw_id_fields = ['section', 'author']
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['discussion', 'author', 'is_solution', 'upvotes', 'created_at']
    list_filter = ['is_solution', 'created_at']
    search_fields = ['content', 'author__username', 'discussion__title']
    raw_id_fields = ['discussion', 'author', 'parent']

@admin.register(CommentVote)
class CommentVoteAdmin(admin.ModelAdmin):
    list_display = ['comment', 'user', 'vote_type', 'created_at']
    list_filter = ['vote_type', 'created_at']
    raw_id_fields = ['comment', 'user']

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ['name', 'badge_type', 'points', 'is_active']
    list_filter = ['badge_type', 'is_active']
    search_fields = ['name', 'description']

@admin.register(StudentBadge)
class StudentBadgeAdmin(admin.ModelAdmin):
    list_display = ['student', 'badge', 'earned_date']
    list_filter = ['earned_date', 'badge']
    search_fields = ['student__roll_number', 'badge__name']
    raw_id_fields = ['student', 'badge']

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['certificate_number', 'student', 'certificate_type', 'title', 'issued_date', 'is_verified']
    list_filter = ['certificate_type', 'is_verified', 'issued_date']
    search_fields = ['certificate_number', 'student__roll_number', 'title']
    raw_id_fields = ['student', 'issued_by']

@admin.register(PeerGroup)
class PeerGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'section', 'created_by', 'is_active', 'get_member_count', 'max_members']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    raw_id_fields = ['section', 'created_by']
    filter_horizontal = ['members']

@admin.register(GroupActivity)
class GroupActivityAdmin(admin.ModelAdmin):
    list_display = ['title', 'group', 'activity_type', 'scheduled_date', 'is_completed']
    list_filter = ['activity_type', 'is_completed', 'scheduled_date']
    search_fields = ['title', 'description', 'group__name']
    raw_id_fields = ['group']