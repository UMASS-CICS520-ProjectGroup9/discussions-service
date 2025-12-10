import os
import sys

# Ensure project root is on sys.path so modules resolve correctly when pytest is
# run from the discussionsService directory.
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

# Set DJANGO_SETTINGS_MODULE early so imports that access django.conf.settings
# don't fail during test collection.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "discussionsService.settings")

import django
django.setup()
