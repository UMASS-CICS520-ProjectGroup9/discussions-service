from django.urls import path
from . import views

urlpatterns = [
    # Discussion endpoints
    path('discussions/', views.discussion_list_create, name='discussion-list-create'),
    path('discussions/<int:pk>/', views.discussion_detail, name='discussion-detail'),

    # Comment endpoints
    path('comments/', views.comment_list_create, name='comment-list-create'),
    path('comments/<int:pk>/', views.comment_detail, name='comment-detail'),

    # Course Discussion endpoints
    path('course-discussions/', views.course_discussion_list_create, name='course-discussion-list-create'),
    path('course-discussions/<int:pk>/', views.course_discussion_detail, name='course-discussion-detail'),
    path('course-discussions/<str:course_subject>/<str:course_id>/', views.course_discussion_by_course_info, name='course-discussion-by-course-info'),

    # Course Comment endpoints
    path('course-comments/', views.course_comment_list_create, name='course-comment-list-create'),
    path('course-comments/<int:pk>/', views.course_comment_detail, name='course-comment-detail'),
]
