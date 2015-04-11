"""
A helper test case class specific for resizing image
"""

import os
import shutil

from django.test import TestCase


# pylint: disable=C0103
class ResizerTestCase(TestCase):
    """
    A testcase more suited for testing images.
    """
    # pylint: disable=E1101
    def remove_dirs(self, dirs):
        """
        Remove some used dirs
        """
        for folder in dirs:
            try:
                shutil.rmtree(os.path.join(self.assets_folder, folder))
            except OSError:
                pass
    # pylint: enable=E1101

    def assertResize(self, image, width, height, msg_prefix=""):
        """
        Passes if the correct resizing with keep op aspect ratio is done

        One size should match, another should be smaller
        """
        if msg_prefix:
            msg_prefix += ": "

        aspect = float(width) / float(height)
        image_aspect = float(image.width) / float(image.height)

        if aspect > image_aspect:
            # Resize target is wider, clip should be on height, width should
            # be less
            if height != image.height:
                msg = ("The height is not the correct size. Should be %ipx, "
                       "but appears to be %ipx." % (height, image.height))
                self.fail(msg)

            if image.width > width:
                msg = ("The width is not the correct size. Should be less "
                       "than %ipx, but appears to be %ipx." %
                       (width, image.width))
                self.fail(msg)
        else:
            # Image is wider, clip should be on width, height should be less
            if width != image.width:
                msg = ("The width is not the correct size. Should be %ipx, "
                       "but appears to be %ipx." % (width, image.width))
                self.fail(msg)

            if image.height > height:
                msg = ("The height is not the correct size. Should be less "
                       "than %ipx, but appears to be %ipx." %
                       (width, image.width))
                self.fail(msg)

    def assertAspectRatio(self, image_1, image_2, decimal_tolerance=2,
                          msg_prefix=""):
        """
        Passes if both images have the same aspect ratio. The number that will
        be compared, will be rounded to the decimal_tolerance parameter
        """
        if msg_prefix:
            msg_prefix += ": "

        ratio_1 = round(float(image_1.width) / float(image_1.height),
                        decimal_tolerance)

        ratio_2 = round(float(image_2.width) / float(image_2.height),
                        decimal_tolerance)

        if ratio_1 != ratio_2:
            msg = "The images ratio's did not match. %s != %s" % (ratio_1,
                                                                  ratio_2)
            self.fail(msg_prefix + msg)

    def assertResizeCrop(self, image, width, height, msg_prefix=""):
        """
        A custom assertion to recalculate the target size of an image
        """
        if msg_prefix:
            msg_prefix += ": "

        if image.width != width:
            msg = ("%sThe image width is %ipx instead of the requested size "
                   "of %ipx." % (msg_prefix, image.width, width))
            self.fail(msg)

        if image.height != height:
            msg = ("%sThe image height is %ipx instead of the requested size "
                   "of %ipx." % (msg_prefix, image.height, height))
            self.fail(msg)
# pylint: enable=C0103
