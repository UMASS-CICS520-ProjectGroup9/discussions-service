from rest_framework import serializers
from django.utils import timezone
from base.models import Discussion, Comment


class CommentSerializer(serializers.ModelSerializer):
    created_at_display = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = '__all__'

    def get_created_at_display(self, obj):
        if not obj.created_at:
            return None
        try:
            # convert to current SITE timezone (settings.TIME_ZONE)
            local = timezone.localtime(obj.created_at)
            return local.strftime('%Y-%m-%d %H:%M')
        except Exception:
            return obj.created_at.isoformat()


class DiscussionSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    created_at_display = serializers.SerializerMethodField()

    class Meta:
        model = Discussion
        fields = '__all__'

    def get_created_at_display(self, obj):
        if not obj.created_at:
            return None
        try:
            local = timezone.localtime(obj.created_at)
            return local.strftime('%Y-%m-%d %H:%M')
        except Exception:
            return obj.created_at.isoformat()
