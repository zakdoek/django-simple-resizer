"""
Resize specific utilities

Future modifications to make:

    - Add animated gif support through gifsicle
    - Do test with wand.Image.transform if more correct (current implementation
      is very brute).
    - Add test with exif data
"""

import os
import math
import tempfile

from contextlib import contextmanager

from wand.image import ORIENTATION_TYPES
from wand.image import Image

from django.core.files.storage import default_storage
from django.core.files.images import ImageFile


def _normalize_params(image, width, height, crop):
    """
    Normalize params and calculate aspect.
    """
    if width is None and height is None:
        raise ValueError("Either width or height must be set. Otherwise "
                         "resizing is useless.")

    if width is None or height is None:
        aspect = float(image.width) / float(image.height)

        if crop:
            raise ValueError("Cropping the image would be useless since only "
                             "one dimention is give to resize along.")

        if width is None:
            width = int(round(height * aspect))
        else:
            height = int(round(width / aspect))

    return (width, height, crop)


def _get_resized_name(image, width, height, crop, namespace):
    """
    Get the name of the resized file when assumed it exists.
    """
    path, name = os.path.split(image.name)
    name_part = "%s/%ix%i" % (namespace, width, height)
    if crop:
        name_part += "_cropped"

    return os.path.join(path, name_part, name)


def _resize(image, width, height, crop):
    """
    Resize the image with respect to the aspect ratio
    """
    ext = os.path.splitext(image.name)[1].strip(".")

    with Image(file=image, format=ext) as b_image:
        # Account for orientation
        if ORIENTATION_TYPES.index(b_image.orientation) > 4:
            # Flip
            target_aspect = float(width) / float(height)
            aspect = float(b_image.height) / float(b_image.width)
        else:
            target_aspect = float(width) / float(height)
            aspect = float(b_image.width) / float(b_image.height)

        # Fix rotation
        b_image.auto_orient()

        # Calculate target size
        target_aspect = float(width) / float(height)
        aspect = float(b_image.width) / float(b_image.height)

        if ((target_aspect > aspect and not crop) or
                (target_aspect <= aspect and crop)):
            # target is wider than image, set height as maximum
            target_height = height

            # calculate width
            # -  iw / ih = tw / th (keep aspect)
            # => th ( iw / ih ) = tw
            target_width = float(target_height) * aspect

            if crop:
                # calculate crop coords
                # -  ( tw - w ) / 2
                target_left = (float(target_width) - float(width)) / 2
                target_left = int(round(target_left))
                target_top = 0

            # correct floating point error, and convert to int, round in the
            # direction of the requested width
            if width >= target_width:
                target_width = int(math.ceil(target_width))
            else:
                target_width = int(math.floor(target_width))
        else:
            # image is wider than target, set width as maximum
            target_width = width

            # calculate height
            # -  iw / ih = tw / th (keep aspect)
            # => tw / ( iw / ih ) = th
            target_height = float(target_width) / aspect

            if crop:
                # calculate crop coords
                # -  ( th - h ) / 2
                target_top = (float(target_height) - float(height)) / 2
                target_top = int(round(target_top))
                target_left = 0

            # correct floating point error and convert to int
            if height >= target_height:
                target_height = int(math.ceil(target_height))
            else:
                target_height = int(math.floor(target_height))

        # strip color profiles
        b_image.strip()

        # Resize
        b_image.resize(target_width, target_height)

        if crop:
            # Crop to target
            b_image.crop(left=target_left, top=target_top, width=width,
                         height=height)

        # Save to temporary file
        temp_file = tempfile.TemporaryFile()
        b_image.save(file=temp_file)
        # Rewind the file
        temp_file.seek(0)
        return temp_file


def resize(image, width=None, height=None, crop=False):
    """
    Resize an image and return the resized file.
    """
    # First normalize params to determine which file to get
    width, height, crop = _normalize_params(image, width, height, crop)

    try:
        # Check the image file state for clean close
        is_closed = image.closed

        if is_closed:
            image.open()

        # Create the resized file
        # Do resize and crop
        resized_image = _resize(image, width, height, crop)
    finally:
        # Re-close if received a closed file
        if is_closed:
            image.close()

    return ImageFile(resized_image)


# pylint: disable=R0913
def resize_lazy(image, width=None, height=None, crop=False, force=False,
                namespace="resized", storage=default_storage,
                as_url=False):
    """
    Returns the name of the resized file. Returns the url if as_url is True
    """
    # First normalize params to determine which file to get
    width, height, crop = _normalize_params(image, width, height, crop)
    # Fetch the name of the resized image so i can test it if exists
    name = _get_resized_name(image, width, height, crop, namespace)

    # Fetch storage if an image has a specific storage
    try:
        storage = image.storage
    except AttributeError:
        pass

    # Test if exists or force
    if force or not storage.exists(name):
        resized_image = None
        try:
            resized_image = resize(image, width, height, crop)
            name = storage.save(name, resized_image)
        finally:
            if resized_image is not None:
                resized_image.close()

    if as_url:
        return storage.url(name)

    return name
# pylint: enable=R0913


@contextmanager
def resized(*args, **kwargs):
    """
    Auto file closing resize function
    """
    resized_image = None
    try:
        resized_image = resize(*args, **kwargs)
        yield resized_image
    finally:
        if resized_image is not None:
            resized_image.close()


from ._version import get_versions  # noqa
__version__ = get_versions()['version']
del get_versions
