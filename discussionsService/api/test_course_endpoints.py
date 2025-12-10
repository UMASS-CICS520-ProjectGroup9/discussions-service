from django.test import TestCase
from rest_framework.test import APIClient
from base.models import CourseDiscussion, CourseComment


class DummyUser:
    def __init__(self, id=None, role=None, is_authenticated=True):
        self.id = id
        self.role = role
        self.is_authenticated = is_authenticated


class CourseEndpointTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # create a course discussion and a comment
        self.discussion = CourseDiscussion.objects.create(title='CD1', body='cb', author='CA', creator_id=10, course_subject='CS', course_id='101')
        self.comment = CourseComment.objects.create(discussion=self.discussion, body='cc1', author='U1', creator_id=1)

    def test_course_discussion_by_course_info_get_and_delete(self):
        # GET should be public (200)
        resp = self.client.get(f'/api/course-discussions/{self.discussion.course_subject}/{self.discussion.course_id}/')
        self.assertEqual(resp.status_code, 200)

        # DELETE requires owner or admin -> unauthenticated should be 403
        resp = self.client.delete(f'/api/course-discussions/{self.discussion.course_subject}/{self.discussion.course_id}/')
        self.assertEqual(resp.status_code, 403)

        # owner can delete
        owner = DummyUser(id=10, role='STUDENT')
        self.client.force_authenticate(user=owner)
        resp = self.client.delete(f'/api/course-discussions/{self.discussion.course_subject}/{self.discussion.course_id}/')
        self.assertIn(resp.status_code, (200, 204))

    def test_course_comment_list_create_get_and_post_auth(self):
        # GET list by discussion id should be private
        resp = self.client.get(f'/api/course-comments/?discussion={self.discussion.id}')
        self.assertEqual(resp.status_code, 403)

        # POST without auth should be forbidden (IsStudent)
        resp = self.client.post('/api/course-comments/', {'discussion': self.discussion.id, 'body': 'x', 'author': 'anon'}, format='json')
        self.assertEqual(resp.status_code, 403)

        # authenticated student can post
        user = DummyUser(id=2, role='STUDENT')
        self.client.force_authenticate(user=user)
        resp = self.client.post('/api/course-comments/', {'discussion': self.discussion.id, 'body': 'x', 'author': 'anon'}, format='json')
        self.assertEqual(resp.status_code, 201)

    def test_course_comment_detail_owner_put_delete(self):
        # GET detail should be public
        resp = self.client.get(f'/api/course-comments/{self.comment.id}/')
        self.assertEqual(resp.status_code, 200)

        # non-owner cannot PUT or DELETE
        non_owner = DummyUser(id=5, role='STUDENT')
        self.client.force_authenticate(user=non_owner)
        resp = self.client.delete(f'/api/course-comments/{self.comment.id}/')
        self.assertEqual(resp.status_code, 403)

        # owner can PUT and DELETE
        owner = DummyUser(id=1, role='STUDENT')
        self.client.force_authenticate(user=owner)
        resp = self.client.put(f'/api/course-comments/{self.comment.id}/', {'body': 'updated', 'discussion': self.discussion.id, 'author': 'U1'}, format='json')
        self.assertEqual(resp.status_code, 200)
        resp = self.client.delete(f'/api/course-comments/{self.comment.id}/')
        self.assertIn(resp.status_code, (200, 204))
