# discussions/forms.py
from django import forms
from .models import Discussion, Comment

class DiscussionForm(forms.ModelForm):
    class Meta:
        model = Discussion
        fields = ['title', 'content', 'category', 'attachment']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter discussion title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Write your discussion...'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'attachment': forms.FileInput(attrs={'class': 'form-control'}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content', 'attachment']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Write your comment...'}),
            'attachment': forms.FileInput(attrs={'class': 'form-control'}),
        }
