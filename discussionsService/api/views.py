from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .permissions import IsAdmin, IsStudent, IsStaff, IsOwnerOrAdmin
from base.models import Discussion, Comment, CourseDiscussion, CourseComment
from .serializers import DiscussionSerializer, CommentSerializer, CourseDiscussionSerializer, CourseCommentSerializer

# Discussion Views
@api_view(['GET', 'POST'])
@permission_classes([IsStudent])
def discussion_list_create(request):
	if request.method == 'GET':
		discussions = Discussion.objects.all().order_by('-created_at')
		serializer = DiscussionSerializer(discussions, many=True)
		return Response(serializer.data)
	elif request.method == 'POST':
		# coerce creator_id before serializer validation so string values won't fail
		data = request.data.copy()
		creator = data.get('creator_id')
		if creator is not None:
			try:
				data['creator_id'] = int(creator)
			except (TypeError, ValueError):
				data['creator_id'] = None

		serializer = DiscussionSerializer(data=data)
		if serializer.is_valid():
			creator = data.get('creator_id')
			if creator is not None:
				serializer.save(creator_id=creator)
			else:
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
		# enforce owner or admin for mutating operations
		if not (discussion.creator_id == getattr(request.user, 'id', None) or getattr(request.user, 'role', '').upper() == 'ADMIN'):
			return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

		serializer = DiscussionSerializer(discussion, data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
	elif request.method == 'DELETE':
		if discussion.creator_id == getattr(request.user, 'id', None) or getattr(request.user, 'role', '').upper() == 'ADMIN':
			discussion.delete()
			return Response(status=status.HTTP_204_NO_CONTENT)
		return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

# Comment Views
@api_view(['GET', 'POST'])
@permission_classes([IsStudent])
def comment_list_create(request):
	if request.method == 'GET':
		discussion_id = request.GET.get('discussion')
		qs = Comment.objects.all()
		if discussion_id:
			# guard against non-integer discussion ids provided by clients
			try:
				q_id = int(discussion_id)
				qs = qs.filter(discussion_id=q_id)
			except (TypeError, ValueError):
				# return empty set for invalid ids instead of raising
				qs = qs.none()
		comments = qs.order_by('-created_at')
		serializer = CommentSerializer(comments, many=True)
		return Response(serializer.data)
	elif request.method == 'POST':
		# copy and coerce incoming data so serializer validation won't fail on bad creator_id
		data = request.data.copy()
		creator = data.get('creator_id')
		if creator is not None:
			try:
				data['creator_id'] = int(creator)
			except (TypeError, ValueError):
				# normalize invalid creator ids to None
				data['creator_id'] = None

		serializer = CommentSerializer(data=data)
		if serializer.is_valid():
			creator = data.get('creator_id')
			if creator is not None:
				serializer.save(creator_id=creator)
			else:
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
		# enforce owner or admin for mutating operations
		if not (comment.creator_id == getattr(request.user, 'id', None) or getattr(request.user, 'role', '').upper() == 'ADMIN'):
			return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

		serializer = CommentSerializer(comment, data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
	elif request.method == 'DELETE':
		if comment.creator_id == getattr(request.user, 'id', None) or getattr(request.user, 'role', '').upper() == 'ADMIN':
			comment.delete()
			return Response(status=status.HTTP_204_NO_CONTENT)
		return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

# Course Discussion Views
@api_view(['GET', 'POST'])
@permission_classes([IsStudent])
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
            creator = getattr(request.user, 'id', None)
            serializer.save(creator_id=creator)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsStudent])
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
        if discussion.creator_id == getattr(request.user, 'id', None) or getattr(request.user, 'role', '').upper() == 'ADMIN':
            discussion.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

@api_view(['GET', 'DELETE'])
@permission_classes([IsOwnerOrAdmin])
def course_discussion_by_course_info(request, course_subject, course_id):
    try:
        discussion = CourseDiscussion.objects.get(course_subject=course_subject, course_id=course_id)
    except CourseDiscussion.DoesNotExist:
        return Response({'error': 'Discussion not found for this course'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CourseDiscussionSerializer(discussion)
        return Response(serializer.data)
    elif request.method == 'DELETE':
        if discussion.creator_id == getattr(request.user, 'id', None) or getattr(request.user, 'role', '').upper() == 'ADMIN':
            discussion.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

# Course Comment Views
@api_view(['GET', 'POST'])
@permission_classes([IsStudent])
def course_comment_list_create(request):
	if request.method == 'GET':
		discussion_id = request.GET.get('discussion')
		course_id = request.GET.get('course_id')
		course_subject = request.GET.get('course_subject')

		print(f"[DEBUG] course_comment_list_create: discussion_id={discussion_id}, course_id={course_id}, course_subject={course_subject}")

		qs = CourseComment.objects.all()

		if discussion_id:
			qs = qs.filter(discussion_id=discussion_id)
		elif course_id and course_subject:
			qs = qs.filter(discussion__course_id=course_id, discussion__course_subject=course_subject)

		print(f"[DEBUG] Filtered CourseComment count: {qs.count()}")

		comments = qs.order_by('-created_at')
		serializer = CourseCommentSerializer(comments, many=True)
		return Response(serializer.data)
	elif request.method == 'POST':
		serializer = CourseCommentSerializer(data=request.data)
		if serializer.is_valid():
			creator = getattr(request.user, 'id', None)
			serializer.save(creator_id=creator)
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsOwnerOrAdmin])
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
        if comment.creator_id == getattr(request.user, 'id', None) or getattr(request.user, 'role', '').upper() == 'ADMIN':
            comment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)