from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from base.models import Discussion, Comment, CourseDiscussion, CourseComment
from .serializers import DiscussionSerializer, CommentSerializer, CourseDiscussionSerializer, CourseCommentSerializer

# Discussion Views
@api_view(['GET', 'POST'])
def discussion_list_create(request):
	if request.method == 'GET':
		discussions = Discussion.objects.all().order_by('-created_at')
		serializer = DiscussionSerializer(discussions, many=True)
		return Response(serializer.data)
	elif request.method == 'POST':
		serializer = DiscussionSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def discussion_detail(request, pk):
	try:
		discussion = Discussion.objects.get(pk=pk)
	except Discussion.DoesNotExist:
		return Response({'error': 'Discussion not found'}, status=status.HTTP_404_NOT_FOUND)

	if request.method == 'GET':
		serializer = DiscussionSerializer(discussion)
		return Response(serializer.data)
	elif request.method == 'PUT':
		serializer = DiscussionSerializer(discussion, data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
	elif request.method == 'DELETE':
		discussion.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)

# Comment Views
@api_view(['GET', 'POST'])
def comment_list_create(request):
	if request.method == 'GET':
		discussion_id = request.GET.get('discussion')
		qs = Comment.objects.all()
		if discussion_id:
			qs = qs.filter(discussion_id=discussion_id)
		comments = qs.order_by('-created_at')
		serializer = CommentSerializer(comments, many=True)
		return Response(serializer.data)
	elif request.method == 'POST':
		serializer = CommentSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def comment_detail(request, pk):
	try:
		comment = Comment.objects.get(pk=pk)
	except Comment.DoesNotExist:
		return Response({'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)

	if request.method == 'GET':
		serializer = CommentSerializer(comment)
		return Response(serializer.data)
	elif request.method == 'PUT':
		serializer = CommentSerializer(comment, data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
	elif request.method == 'DELETE':
		comment.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)


# Course Discussion Views
@api_view(['GET', 'POST'])
def course_discussion_list_create(request):
	if request.method == 'GET':
		course_id = request.GET.get('course_id')
		course_subject = request.GET.get('course_subject')
		qs = CourseDiscussion.objects.all()
		if course_id and course_subject:
			qs = qs.filter(course_id=course_id, course_subject=course_subject)
		discussions = qs.order_by('-created_at')
		serializer = CourseDiscussionSerializer(discussions, many=True)
		return Response(serializer.data)
	elif request.method == 'POST':
		serializer = CourseDiscussionSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def course_discussion_detail(request, pk):
	try:
		discussion = CourseDiscussion.objects.get(pk=pk)
	except CourseDiscussion.DoesNotExist:
		return Response({'error': 'Discussion not found'}, status=status.HTTP_404_NOT_FOUND)

	if request.method == 'GET':
		serializer = CourseDiscussionSerializer(discussion)
		return Response(serializer.data)
	elif request.method == 'PUT':
		serializer = CourseDiscussionSerializer(discussion, data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
	elif request.method == 'DELETE':
		discussion.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)
@api_view(['GET', 'DELETE'])
def course_discussion_by_course_info(request, course_subject, course_id):
    try:
        discussion = CourseDiscussion.objects.get(course_subject=course_subject, course_id=course_id)
    except CourseDiscussion.DoesNotExist:
        return Response({'error': 'Discussion not found for this course'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CourseDiscussionSerializer(discussion)
        return Response(serializer.data)
    elif request.method == 'DELETE':
        discussion.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Course Comment Views
@api_view(['GET', 'POST'])
def course_comment_list_create(request):
	if request.method == 'GET':
		discussion_id = request.GET.get('discussion')
		course_id = request.GET.get('course_id')
		course_subject = request.GET.get('course_subject')

		qs = CourseComment.objects.all()

		if discussion_id:
			qs = qs.filter(discussion_id=discussion_id)
		elif course_id and course_subject:
			qs = qs.filter(discussion__course_id=course_id, discussion__course_subject=course_subject)

		comments = qs.order_by('-created_at')
		serializer = CourseCommentSerializer(comments, many=True)
		return Response(serializer.data)
	elif request.method == 'POST':
		serializer = CourseCommentSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def course_comment_detail(request, pk):
	try:
		comment = CourseComment.objects.get(pk=pk)
	except CourseComment.DoesNotExist:
		return Response({'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)

	if request.method == 'GET':
		serializer = CourseCommentSerializer(comment)
		return Response(serializer.data)
	elif request.method == 'PUT':
		serializer = CourseCommentSerializer(comment, data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
	elif request.method == 'DELETE':
		comment.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)
