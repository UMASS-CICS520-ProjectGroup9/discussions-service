from django.test import TestCase
from rest_framework.test import APIClient
from base.models import Discussion, Comment
from django.utils import timezone


class DummyUser:
    def __init__(self, id=None, role=None, is_authenticated=True):
        self.id = id
        self.role = role
        self.is_authenticated = is_authenticated


class CommentEndpointTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # base discussion and comments
        self.discussion = Discussion.objects.create(title='D1', body='b', author='A', creator_id=10)
        # comment owned by user with creator_id=1
        self.comment = Comment.objects.create(discussion=self.discussion, body='c1', author='U1', creator_id=1)


    def test_create_with_invalid_discussion_fk(self):
        user = DummyUser(id=2, role='STUDENT')
        self.client.force_authenticate(user=user)

        # Use a non-existent discussion id
        resp = self.client.post('/api/comments/', {'discussion': 999999, 'body': 'x', 'author': 'a'}, format='json')
        self.assertEqual(resp.status_code, 400)

    def test_create_with_invalid_creator_id_string_results_null(self):
        user = DummyUser(id=3, role='STUDENT')
        self.client.force_authenticate(user=user)

        payload = {'discussion': self.discussion.id, 'body': 'hello', 'author': 'Bob', 'creator_id': 'not-an-int'}
        resp = self.client.post('/api/comments/', payload, format='json')
        self.assertEqual(resp.status_code, 201)
        # verify stored creator_id is null
        created_id = resp.data.get('id')
        c = Comment.objects.get(pk=created_id)
        self.assertIsNone(c.creator_id)

    def test_put_partial_vs_full_behavior(self):
        # owner attempts partial PUT (missing required fields) => 400
        owner = DummyUser(id=1, role='STUDENT')
        self.client.force_authenticate(user=owner)

        resp = self.client.put(f'/api/comments/{self.comment.id}/', {'body': 'newbody'}, format='json')
        # serializer requires all fields for PUT (no partial=True)
        self.assertEqual(resp.status_code, 400)

        # full PUT with all required fields should succeed
        full_payload = {'discussion': self.discussion.id, 'body': 'newbody', 'author': 'U1'}
        resp = self.client.put(f'/api/comments/{self.comment.id}/', full_payload, format='json')
        self.assertIn(resp.status_code, (200,))
        self.assertEqual(resp.data['body'], 'newbody')

    def test_non_owner_cannot_put_or_delete(self):
        non_owner = DummyUser(id=4, role='STUDENT')
        self.client.force_authenticate(user=non_owner)

        # non-owner PUT
        resp = self.client.put(f'/api/comments/{self.comment.id}/', {'discussion': self.discussion.id, 'body': 'x', 'author': 'Y'}, format='json')
        self.assertEqual(resp.status_code, 403)

        # non-owner DELETE
        resp = self.client.delete(f'/api/comments/{self.comment.id}/')
        self.assertEqual(resp.status_code, 403)

    def test_ordering_multiple_comments(self):
        user = DummyUser(id=5, role='STUDENT')
        self.client.force_authenticate(user=user)

        # create two comments, second should be first in list due to -created_at
        c1 = Comment.objects.create(discussion=self.discussion, body='first', author='A')
        # ensure different timestamp
        c2 = Comment.objects.create(discussion=self.discussion, body='second', author='B')

        resp = self.client.get(f'/api/comments/?discussion={self.discussion.id}')
        self.assertEqual(resp.status_code, 200)
        bodies = [c['body'] for c in resp.data]
        # newest (c2) should appear before c1
        self.assertTrue(bodies.index('second') < bodies.index('first'))

    def test_large_body_handling(self):
        user = DummyUser(id=6, role='STUDENT')
        self.client.force_authenticate(user=user)

        large = 'x' * 100000
        resp = self.client.post('/api/comments/', {'discussion': self.discussion.id, 'body': large, 'author': 'Large'}, format='json')
        # Should create or at least not crash; expect 201
        self.assertEqual(resp.status_code, 201)

    def test_delete_then_get_returns_404(self):
        owner = DummyUser(id=1, role='STUDENT')
        self.client.force_authenticate(user=owner)

        resp = self.client.delete(f'/api/comments/{self.comment.id}/')
        self.assertIn(resp.status_code, (200, 204))

        # subsequent GET should be 404
        resp = self.client.get(f'/api/comments/{self.comment.id}/')
        self.assertEqual(resp.status_code, 404)

    def test_required_fields_validation(self):
        user = DummyUser(id=7, role='STUDENT')
        self.client.force_authenticate(user=user)

        # missing body
        resp = self.client.post('/api/comments/', {'discussion': self.discussion.id, 'author': 'A'}, format='json')
        self.assertEqual(resp.status_code, 400)

        # missing author
        resp = self.client.post('/api/comments/', {'discussion': self.discussion.id, 'body': 'b'}, format='json')
        self.assertEqual(resp.status_code, 400)

    def test_filter_with_non_int_discussion_param(self):
        user = DummyUser(id=8, role='STUDENT')
        self.client.force_authenticate(user=user)

        resp = self.client.get('/api/comments/?discussion=notanint')
        # should not crash; return 200 and usually empty list
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.data, list)

    def test_response_fields_present(self):
        user = DummyUser(id=9, role='STUDENT')
        self.client.force_authenticate(user=user)

        resp = self.client.get(f'/api/comments/?discussion={self.discussion.id}')
        self.assertEqual(resp.status_code, 200)
        if resp.data:
            item = resp.data[0]
            self.assertIn('created_at_display', item)
            self.assertIn('discussion_title', item)

