from django.test import TestCase
from base.models import Discussion, Comment
from .serializers import DiscussionSerializer, CommentSerializer
from django.utils import timezone


class SerializerTests(TestCase):
    def test_discussion_and_comment_serialization(self):
        # create a discussion
        d = Discussion.objects.create(title='Test', body='Body', author='Alice')
        # create a comment
        c = Comment.objects.create(discussion=d, body='Nice', author='Bob')

        # refresh
        d.refresh_from_db()
        c.refresh_from_db()

        ds = DiscussionSerializer(d)
        data = ds.data

        # Discussion serializer should include comments and created_at_display
        self.assertIn('comments', data)
        self.assertIn('created_at_display', data)
        self.assertIsInstance(data['comments'], list)

        cs = CommentSerializer(c)
        cdata = cs.data
        self.assertIn('discussion_title', cdata)
        self.assertEqual(cdata['discussion_title'], d.title)
        self.assertIn('created_at_display', cdata)

    def test_created_at_display_none_and_format(self):
        # create discussion without created_at (it will be auto-set by DB) - but test None behavior by constructing object
        d = Discussion(title='NoTime', body='b', author='Z')
        # not saved, created_at is None. Don't call serializer.data (it accesses related managers).
        # Instead call the serializer method directly.
        serializer = DiscussionSerializer()
        self.assertIsNone(serializer.get_created_at_display(d))

        # saved object should have created_at and formatted string
        d.save()
        ds = DiscussionSerializer(d)
        data = ds.data
        self.assertIsNotNone(data.get('created_at_display'))

    def test_created_at_display_fallback_on_exception(self):
        # create and save a comment, then monkeypatch timezone.localtime to raise
        d = Discussion.objects.create(title='T', body='b', author='A')
        c = Comment.objects.create(discussion=d, body='x', author='y')

        original_localtime = timezone.localtime

        def bad_localtime(dt):
            raise RuntimeError('boom')

        try:
            timezone.localtime = bad_localtime
            cs = CommentSerializer(c)
            data = cs.data
            # fallback should provide ISO format
            self.assertIn('created_at_display', data)
            self.assertTrue('T' in data['created_at_display'] or data['created_at_display'].count('-') >= 2)
        finally:
            timezone.localtime = original_localtime

    def test_course_serializers_include_comments(self):
        from base.models import CourseDiscussion, CourseComment

        cd = CourseDiscussion.objects.create(course_id='101', course_subject='CS', title='C', body='b', author='A')
        cc = CourseComment.objects.create(discussion=cd, body='cm', author='B')

        from .serializers import CourseDiscussionSerializer, CourseCommentSerializer

        cds = CourseDiscussionSerializer(cd)
        data = cds.data
        self.assertIn('comments', data)
        self.assertIsInstance(data['comments'], list)

