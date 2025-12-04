from django.db import models

class Discussion(models.Model):
	title = models.CharField(max_length=200)
	body = models.TextField()
	author = models.CharField(max_length=100)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.title

class Comment(models.Model):
	discussion = models.ForeignKey(Discussion, related_name='comments', on_delete=models.CASCADE)
	body = models.TextField()
	author = models.CharField(max_length=100)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f"Comment by {self.author} on {self.discussion.title}"

# for course
class CourseDiscussion(models.Model):
	course_id = models.CharField(max_length=100)
	course_subject = models.CharField(max_length=100)
	title = models.CharField(max_length=200)
	body = models.TextField()
	author = models.CharField(max_length=100)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		unique_together = ('course_id', 'course_subject')

	def __str__(self):
		return f"{self.course_subject} {self.course_id}: {self.title}"

class CourseComment(models.Model):
	discussion = models.ForeignKey(CourseDiscussion, related_name='comments', on_delete=models.CASCADE)
	body = models.TextField()
	author = models.CharField(max_length=100)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f"Comment by {self.author} on {self.discussion.title}"
