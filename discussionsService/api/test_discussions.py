from django.test import TestCase
from rest_framework.test import APIClient
from base.models import Discussion, Comment


class DummyUser:
    def __init__(self, id=None, role=None, is_authenticated=True):
        self.id = id
        self.role = role
        self.is_authenticated = is_authenticated


class DiscussionEndpointTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # create an existing discussion owned by user id=1
        self.owner_discussion = Discussion.objects.create(title='Owner', body='owned', author='Owner', creator_id=1)

    def test_list_and_create_discussion_as_student(self):
        user = DummyUser(id=2, role='STUDENT')
        self.client.force_authenticate(user=user)

        # GET list
        resp = self.client.get('/api/discussions/')
        self.assertEqual(resp.status_code, 200)

        # POST create
        payload = {'title': 'New', 'body': 'body', 'author': 'Alice'}
        resp = self.client.post('/api/discussions/', payload, format='json')
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data['title'], 'New')

    def test_get_put_delete_permissions(self):
        # Non-owner non-admin cannot delete
        non_owner = DummyUser(id=3, role='STUDENT')
        self.client.force_authenticate(user=non_owner)

        # try to delete owner's discussion
        resp = self.client.delete(f'/api/discussions/{self.owner_discussion.id}/')
        self.assertEqual(resp.status_code, 403)

        # owner can delete
        owner = DummyUser(id=1, role='STUDENT')
        self.client.force_authenticate(user=owner)
        resp = self.client.delete(f'/api/discussions/{self.owner_discussion.id}/')
        self.assertIn(resp.status_code, (200, 204))

    def test_admin_can_delete_any(self):
        admin = DummyUser(id=99, role='ADMIN')
        # recreate discussion to ensure it exists
        d = Discussion.objects.create(title='X', body='b', author='A', creator_id=5)
        self.client.force_authenticate(user=admin)
        resp = self.client.delete(f'/api/discussions/{d.id}/')
        self.assertIn(resp.status_code, (200, 204))

    def test_create_with_invalid_creator_id(self):
        user = DummyUser(id=4, role='STUDENT')
        self.client.force_authenticate(user=user)

        payload = {'title': 'T2', 'body': 'B2', 'author': 'Z', 'creator_id': 'notanint'}
        resp = self.client.post('/api/discussions/', payload, format='json')
        # view attempts to coerce creator_id; invalid should be normalized to None and succeed
        self.assertEqual(resp.status_code, 201)

    def test_put_requires_owner_or_admin(self):
        # create a discussion by user 10
        d = Discussion.objects.create(title='Owner2', body='b', author='A', creator_id=10)

        non_owner = DummyUser(id=11, role='STUDENT')
        self.client.force_authenticate(user=non_owner)
        resp = self.client.put(f'/api/discussions/{d.id}/', {'title': 'X', 'body': 'Y', 'author': 'A'}, format='json')
        self.assertEqual(resp.status_code, 403)

        owner = DummyUser(id=10, role='STUDENT')
        self.client.force_authenticate(user=owner)
        resp = self.client.put(f'/api/discussions/{d.id}/', {'title': 'X2', 'body': 'Y2', 'author': 'A'}, format='json')
        self.assertEqual(resp.status_code, 200)

    def test_ordering_and_lifecycle(self):
        user = DummyUser(id=20, role='STUDENT')
        self.client.force_authenticate(user=user)

        d1 = Discussion.objects.create(title='d1', body='b1', author='a', creator_id=20)
        d2 = Discussion.objects.create(title='d2', body='b2', author='b', creator_id=20)

        resp = self.client.get('/api/discussions/')
        self.assertEqual(resp.status_code, 200)
        titles = [x['title'] for x in resp.data]
        # newest should appear first
        self.assertTrue(titles.index('d2') < titles.index('d1'))

        # delete one then ensure detail returns 404
        resp = self.client.delete(f'/api/discussions/{d1.id}/')
        # user 20 is owner so delete should be allowed
        self.assertIn(resp.status_code, (200, 204))
        resp = self.client.get(f'/api/discussions/{d1.id}/')
        self.assertEqual(resp.status_code, 404)

    def test_missing_required_fields_on_create(self):
        user = DummyUser(id=21, role='STUDENT')
        self.client.force_authenticate(user=user)

        # missing title
        resp = self.client.post('/api/discussions/', {'body': 'b', 'author': 'a'}, format='json')
        self.assertEqual(resp.status_code, 400)

        # missing body
        resp = self.client.post('/api/discussions/', {'title': 't', 'author': 'a'}, format='json')
        self.assertEqual(resp.status_code, 400)

