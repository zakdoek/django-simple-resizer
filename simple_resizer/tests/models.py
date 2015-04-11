"""
Some models purely for testing
"""

from django.db import models
from django.core.files.storage import FileSystemStorage


def _get_storage():
    """
    Create a filesystemstorage
    """
    return FileSystemStorage(location="simple_resizer/tests/assets/",
                             base_url="http://www.example.com/my/storage/")


class ResizeTestModel(models.Model):
    """
    A model with an imagefield purely for testing

    Will use a custom storage
    """
    image = models.ImageField(upload_to="resize_test_model/images/",
                              storage=_get_storage())
