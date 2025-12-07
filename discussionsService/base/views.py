
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from base.models import Discussion, Comment
from .serializers import DiscussionSerializer, CommentSerializer

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
