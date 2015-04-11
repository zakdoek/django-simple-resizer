"""
Test for the gallery.utils.render module
"""

import os
import shutil

from django.core.files.images import ImageFile
from django.core.files.storage import default_storage

from ..utils.test import ResizerTestCase
import resizer as resize

from .models import ResizeTestModel


def get_test_directory():
    """
    returns the test directory
    """
    return os.path.dirname(__file__)


# pylint: disable=E1101
class ResizeTest(ResizerTestCase):
    """
    Test the render method
    """
    @classmethod
    def setUpClass(cls):
        """
        Set up class based
        """
        cls.assets_folder = os.path.join(get_test_directory(), "assets")
        cls.image_paths = (
            os.path.join(cls.assets_folder, "image-1.jpg"),
            os.path.join(cls.assets_folder, "image-2.png"))

    def setUp(self):
        """
        Setup the test resources
        """
        for idx, image_path in enumerate(self.image_paths):
            with open(image_path, "r") as image_file:
                setattr(self, "image_%i" % (idx + 1), ImageFile(image_file))

    def tearDown(self):
        """
        Teardown the test
        """
        for idx in range(1, len(self.image_paths) + 1):
            getattr(self, "image_%i" % idx).close()

        self.remove_dirs(("resized", "resize_test_model",))

    def test_file_resize_jpeg(self):
        """
        Test file resize jpeg
        """
        with resize.resized(self.image_1, 1000, 500) as image:
            self.assertResize(image, 1000, 500)
            self.assertAspectRatio(image, self.image_1)
            self.assertLessEqual(image.size, self.image_1.size)

    def test_file_resize_png(self):
        """
        Test file resize png
        """
        with resize.resized(self.image_2, 500, 500) as image:
            self.assertResize(image, 500, 500)
            self.assertAspectRatio(image, self.image_2)
            self.assertLessEqual(image.size, self.image_2.size)

    def test_file_resize_crop_jpeg(self):
        """
        Test file resize and crop for jpeg
        """
        with resize.resized(self.image_1, 1000, 500, crop=True) as image:
            self.assertResizeCrop(image, 1000, 500)
            self.assertLessEqual(image.size, self.image_1.size)

    def test_file_resize_crop_png(self):
        """
        Test file resize and crop for png
        """
        with resize.resized(self.image_2, 500, 500, crop=True) as image:
            self.assertResizeCrop(image, 500, 500)
            self.assertLessEqual(image.size, self.image_2.size)

    def test_file_resize_lazy(self):
        """
        Test a lazy resize for:
            - url
            - name
            - modified date
            - custom storage
        """
        resized_name = resize.resize_lazy(self.image_1, 500, 500)
        image = ImageFile(default_storage.open(resized_name))
        self.assertResize(image, 500, 500)
        self.assertAspectRatio(image, self.image_1)
        resized_name_bis = resize.resize_lazy(self.image_1, 500, 500)
        self.assertEqual(resized_name_bis, resized_name)
        resized_url = resize.resize_lazy(self.image_1, 500, 500, as_url=True)
        self.assertEqual(resized_url, default_storage.url(resized_name))
        image_2 = default_storage.open(resized_name_bis)
        self.assertEqual(default_storage.modified_time(resized_name),
                         default_storage.modified_time(resized_name_bis))
        image.close()
        image_2.close()
        default_storage.delete(resized_name)

    def test_file_resize_only_width(self):
        """
        Test the way the engine assumes parameters that are not given
        """
        with resize.resized(self.image_1, 500) as image:
            self.assertEqual(image.width, 500)
            self.assertAspectRatio(image, self.image_1)

    def test_file_resize_only_height(self):
        """
        Test the resizer when no width is given
        """
        with resize.resized(self.image_1, height=500) as image:
            self.assertEqual(image.height, 500)
            self.assertAspectRatio(image, self.image_1)

    def test_file_resize_crop_omitted(self):
        """
        Test crop when only one dimention is given
        """
        with self.assertRaises(ValueError):
            with resize.resized(self.image_1, 500, crop=True) as dummy:
                pass

        with self.assertRaises(ValueError):
            with resize.resized(self.image_1, height=500, crop=True) as dummy:
                pass

    def test_omit_dimentions(self):
        """
        Test when no parameters are given
        """
        with self.assertRaises(ValueError):
            with resize.resized(self.image_1) as dummy:
                pass

    def test_model_resize(self):
        """
        Test the resizing on a model
        """
        self.image_1.open()
        model = ResizeTestModel(image=self.image_1)
        model.save()

        with resize.resized(model.image, 500, 500) as image:
            self.assertResize(image, 500, 500)
            self.assertAspectRatio(image, model.image)
            self.assertLessEqual(image.size, model.image.size)

    def test_model_resize_lazy(self):
        """
        Test lazy resizing on a model
        """
        self.image_1.open()
        model = ResizeTestModel(image=self.image_1)
        model.save()

        loaded_model = ResizeTestModel.objects.get(pk=model.pk)

        resized_name = resize.resize_lazy(loaded_model.image, 500, 500)
        image = ImageFile(model.image.storage.open(resized_name))
        self.assertResize(image, 500, 500)
        self.assertAspectRatio(image, loaded_model.image)
        self.assertLessEqual(image.size, loaded_model.image.size)

        image.close()
# pylint: enable=E1101
