import os
import sys


def setup_django(settings=None, project_path=None):
    # Update Python path
    sys.path = [project_path or os.getcwd()] + sys.path
    # Setup django module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings)
    # Setup django
    # noinspection PyPackageRequirements
    import django
    # noinspection PyUnresolvedReferences
    django.setup()
