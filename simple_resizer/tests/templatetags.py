"""
Run some tests on the template tags

These tests should:
    - Point check if a correct url is produced
    - If the url points to the file
    - If the file pointed to is actually resized
    - If resizing occurs lazy
    - In case of a model image field
    - In case of an image field
    - Do this for both template tags
"""

import os

from django.template import Template
from django.template import Context
from django.core.files.images import ImageFile
from django.core.files.storage import default_storage

from ..utils.test import ResizerTestCase

from .models import ResizeTestModel

from . import get_test_directory


class ResizeTemplateTag(ResizerTestCase):
    """
    Test the resize template tag
    """
    def setUp(self):
        """
        Setup the test
        """
        load_tag = "{% load resize from simple_resizer %}"
        render_url = "{% resize image=image width=300 height=300 %}"
        self.template = Template("".join((load_tag, render_url)))
        self.assets_folder = os.path.join(get_test_directory(), "assets")
        self.image_path = os.path.join(self.assets_folder, "image-1.jpg")

        with open(self.image_path, "rb") as image_file:
            self.image_1 = ImageFile(image_file)

        self.image_1.open()
        self.model = ResizeTestModel(image=self.image_1)
        self.model.save()
        self.image_1.close()

    def tearDown(self):
        """
        Cleanup some stuff
        """
        self.image_1.close()

        self.remove_dirs(("resized", "resize_test_model"))

    def test_resize(self):
        """
        Test the plain resize tag
        """
        rendered = self.template.render(Context({"image": self.image_1}))

        image = ImageFile(default_storage.open(rendered))

        self.assertResize(image, 300, 300)
        self.assertAspectRatio(image, self.image_1)
        self.assertLessEqual(image.size, self.image_1.size)

        image.close()

    def test_model_resize(self):
        """
        Test the template tag with an imagefield
        """
        rendered = self.template.render(Context({"image": self.model.image}))

        self.assertIn("http://www.example.com/my/storage/", rendered)


# pylint: disable=R0902
class ConditionalResizeTemplateTagTest(ResizerTestCase):
    """
    Test the resize template tag
    """
    def setUp(self):
        """
        Setup the test
        """
        load_tag = "{% load conditional_resize from simple_resizer %}"
        render_url = ("{% conditional_resize image=image width=300 "
                      "height=300 ratio=1.3 %}")
        self.template = Template("".join((load_tag, render_url)))
        self.assets_folder = os.path.join(get_test_directory(), "assets")
        self.image_path_1 = os.path.join(self.assets_folder, "image-1.jpg")
        self.image_path_2 = os.path.join(self.assets_folder, "image-2.png")

        with open(self.image_path_1, "rb") as image_file:
            self.image_1 = ImageFile(image_file)

        with open(self.image_path_2, "rb") as image_file:
            self.image_2 = ImageFile(image_file)

        self.image_1.open()
        self.model = ResizeTestModel(image=self.image_1)
        self.model.save()
        self.image_1.close()

        self.image_2.open()
        self.model_2 = ResizeTestModel(image=self.image_2)
        self.model_2.save()
        self.image_2.close()

    def tearDown(self):
        """
        Cleanup some stuff
        """
        self.image_1.close()
        self.image_2.close()

        self.remove_dirs(("resized", "resize_test_model"))

    def test_conditional_resize(self):
        """
        Test the plain resize tag
        """
        rendered = self.template.render(Context({"image": self.image_1}))

        image = ImageFile(default_storage.open(rendered))

        self.assertEqual(image.height, 300)
        self.assertLess(image.width, 300)

        image.close()

        rendered = self.template.render(Context({"image": self.image_2}))

        image = ImageFile(default_storage.open(rendered))

        self.assertEqual(image.width, 300)

        image.close()

    def test_model_conditional_resize(self):
        """
        Test the template tag with an imagefield
        """
        rendered = self.template.render(Context({"image": self.model.image}))
        self.assertIn("http://www.example.com/my/storage/", rendered)

        rendered = self.template.render(Context({"image": self.model_2.image}))
        self.assertIn("http://www.example.com/my/storage/", rendered)
# pylint: enable=R0902
