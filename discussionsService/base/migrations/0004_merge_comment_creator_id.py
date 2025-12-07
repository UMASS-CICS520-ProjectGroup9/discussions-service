"""Merge migration to resolve multiple leaf nodes in base migrations."""
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0002_comment_creator_id_discussion_creator_id"),
        ("base", "0003_comment_creator_id_coursecomment_creator_id_and_more"),
    ]

    operations = []
"""Merge migration to resolve multiple leaf nodes in base migrations."""
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0002_comment_creator_id_discussion_creator_id"),
        ("base", "0003_comment_creator_id_coursecomment_creator_id_and_more"),
    ]

    operations = []
