from django.urls import path
from . import views

urlpatterns = [
    # Discussion forum
    path('<int:section_id>/', views.discussion_list, name='discussion_list'),
    path('<int:section_id>/create/', views.discussion_create, name='discussion_create'),
    path('discussion/<int:pk>/', views.discussion_detail, name='discussion_detail'),
    path('discussion/<int:pk>/edit/', views.discussion_edit, name='discussion_edit'),
    path('discussion/<int:pk>/delete/', views.discussion_delete, name='discussion_delete'),
    path('discussion/<int:pk>/toggle-pin/', views.discussion_toggle_pin, name='discussion_toggle_pin'),
    path('discussion/<int:pk>/toggle-lock/', views.discussion_toggle_lock, name='discussion_toggle_lock'),
    path('discussion/<int:pk>/resolve/', views.discussion_resolve, name='discussion_resolve'),
    
    # Comments
    path('discussion/<int:discussion_id>/comment/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('comment/<int:comment_id>/vote/', views.vote_comment, name='vote_comment'),
    path('comment/<int:comment_id>/mark-solution/', views.mark_solution, name='mark_solution'),
]