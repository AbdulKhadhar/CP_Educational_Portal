from django.db import models
from django.utils.text import slugify
from accounts.models import User
from colleges.models import ClassSection, Student

class Discussion(models.Model):
    CATEGORY_CHOICES = (
        ('general', 'General Discussion'),
        ('doubt', 'Doubt/Question'),
        ('announcement', 'Announcement'),
        ('resource', 'Resource Sharing'),
        ('feedback', 'Feedback'),
    )
    
    section = models.ForeignKey(ClassSection, on_delete=models.CASCADE, related_name='discussions')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='discussions')
    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=350, blank=True)
    content = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    is_pinned = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    is_resolved = models.BooleanField(default=False)
    views_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    attachment = models.FileField(upload_to='discussions/', blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-is_pinned', '-created_at']


class Comment(models.Model):
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    is_solution = models.BooleanField(default=False)
    upvotes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    attachment = models.FileField(upload_to='comments/', blank=True, null=True)
    
    def __str__(self):
        return f"Comment by {self.author.get_full_name()} on {self.discussion.title}"
    
    class Meta:
        ordering = ['-is_solution', '-created_at']


class CommentVote(models.Model):
    VOTE_CHOICES = (
        (1, 'Upvote'),
        (-1, 'Downvote'),
    )
    
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_votes')
    vote_type = models.IntegerField(choices=VOTE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_vote_type_display()}"
    
    class Meta:
        unique_together = ['comment', 'user']


class Badge(models.Model):
    BADGE_TYPES = (
        ('participation', 'Participation'),
        ('achievement', 'Achievement'),
        ('excellence', 'Excellence'),
        ('consistency', 'Consistency'),
        ('special', 'Special'),
    )
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    badge_type = models.CharField(max_length=20, choices=BADGE_TYPES)
    icon = models.ImageField(upload_to='badges/', blank=True, null=True)
    criteria = models.JSONField(default=dict)
    points = models.IntegerField(default=10)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class StudentBadge(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name='awarded_to')
    earned_date = models.DateField(auto_now_add=True)
    reason = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.student.roll_number} - {self.badge.name}"
    
    class Meta:
        unique_together = ['student', 'badge']
        ordering = ['-earned_date']


class Certificate(models.Model):
    CERTIFICATE_TYPES = (
        ('participation', 'Participation Certificate'),
        ('excellence', 'Certificate of Excellence'),
        ('completion', 'Course Completion'),
        ('achievement', 'Special Achievement'),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='certificates')
    certificate_type = models.CharField(max_length=20, choices=CERTIFICATE_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    issued_date = models.DateField(auto_now_add=True)
    certificate_number = models.CharField(max_length=50, unique=True)
    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='issued_certificates')
    pdf_file = models.FileField(upload_to='certificates/', blank=True, null=True)
    is_verified = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.title} - {self.student.roll_number}"
    
    def save(self, *args, **kwargs):
        if not self.certificate_number:
            import uuid
            self.certificate_number = f"CERT-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-issued_date']


class PeerGroup(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    section = models.ForeignKey(ClassSection, on_delete=models.CASCADE, related_name='peer_groups')
    members = models.ManyToManyField(Student, related_name='peer_groups')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_groups')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    max_members = models.IntegerField(default=5)
    
    def __str__(self):
        return f"{self.name} - {self.section}"
    
    def get_member_count(self):
        return self.members.count()
    
    class Meta:
        ordering = ['name']


class GroupActivity(models.Model):
    ACTIVITY_TYPES = (
        ('meeting', 'Group Meeting'),
        ('discussion', 'Discussion'),
        ('project', 'Project Work'),
        ('study', 'Study Session'),
    )
    
    group = models.ForeignKey(PeerGroup, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    scheduled_date = models.DateTimeField()
    duration_minutes = models.IntegerField()
    location = models.CharField(max_length=200, blank=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.group.name}"
    
    class Meta:
        ordering = ['-scheduled_date']
        verbose_name_plural = 'Group Activities'