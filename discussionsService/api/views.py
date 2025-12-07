from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .permissions import IsAdmin, IsStudent, IsStaff, IsOwnerOrAdmin
from rest_framework.permissions import AllowAny
from base.models import Discussion, Comment, CourseDiscussion, CourseComment
from .serializers import DiscussionSerializer, CommentSerializer, CourseDiscussionSerializer, CourseCommentSerializer

# Discussion Views
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def discussion_list_create(request):
	if request.method == 'GET':
		discussions = Discussion.objects.all().order_by('-created_at')
		serializer = DiscussionSerializer(discussions, many=True)
		return Response(serializer.data)
	elif request.method == 'POST':
		serializer = DiscussionSerializer(data=request.data)
		if serializer.is_valid():
			# if client provided creator_id (from website session), persist it
			creator = request.data.get('creator_id')
			if creator is not None:
				try:
					creator = int(creator)
				except (TypeError, ValueError):
					creator = None
				serializer.save(creator_id=creator)
			else:
				serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
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
		# Owner-only delete enforcement
		# Expect client to provide X-User-ID header (sent from website service)
		requester_id = request.headers.get('X-User-ID')
		creator_id = discussion.creator_id
		# If we have a creator_id recorded, require it to match the requester
		if creator_id is not None:
			try:
				creator_id_int = int(creator_id)
			except (TypeError, ValueError):
				creator_id_int = None
			try:
				requester_id_int = int(requester_id) if requester_id is not None else None
			except (TypeError, ValueError):
				requester_id_int = None
			if creator_id_int is None or requester_id_int is None or creator_id_int != requester_id_int:
				return Response({'error': 'Forbidden: only the creator can delete this discussion.'}, status=status.HTTP_403_FORBIDDEN)
		discussion.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)

# Comment Views
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
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
			creator = request.data.get('creator_id')
			if creator is not None:
				try:
					creator = int(creator)
				except (TypeError, ValueError):
					creator = None
				serializer.save(creator_id=creator)
			else:
				serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
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
		# Owner-only delete enforcement for comments
		requester_id = request.headers.get('X-User-ID')
		creator_id = comment.creator_id
		if creator_id is not None:
			try:
				creator_id_int = int(creator_id)
			except (TypeError, ValueError):
				creator_id_int = None
			try:
				requester_id_int = int(requester_id) if requester_id is not None else None
			except (TypeError, ValueError):
				requester_id_int = None
			if creator_id_int is None or requester_id_int is None or creator_id_int != requester_id_int:
				return Response({'error': 'Forbidden: only the creator can delete this comment.'}, status=status.HTTP_403_FORBIDDEN)
		comment.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)


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
@permission_classes([IsOwnerOrAdmin])
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
@permission_classes([IsStudent])
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
