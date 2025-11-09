from django.urls import path
from . import views

urlpatterns = [
    # Discussion endpoints
    path('discussions/', views.discussion_list_create, name='discussion-list-create'),
    path('discussions/<int:pk>/', views.discussion_detail, name='discussion-detail'),

    # Comment endpoints
    path('comments/', views.comment_list_create, name='comment-list-create'),
    path('comments/<int:pk>/', views.comment_detail, name='comment-detail'),
]
