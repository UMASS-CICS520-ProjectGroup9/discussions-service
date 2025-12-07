
from django.db import models

class Discussion(models.Model):
	title = models.CharField(max_length=200)
	body = models.TextField()
	author = models.CharField(max_length=100)
	# optional external user id who created this discussion
	creator_id = models.IntegerField(null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.title

class Comment(models.Model):
	discussion = models.ForeignKey(Discussion, related_name='comments', on_delete=models.CASCADE)
	body = models.TextField()
	author = models.CharField(max_length=100)
	# optional external user id who created this comment
	creator_id = models.IntegerField(null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f"Comment by {self.author} on {self.discussion.title}"
