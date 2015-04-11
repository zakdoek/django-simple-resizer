"""
Resizing template tags
"""

from django import template

from .. import resize_lazy

register = template.Library()  # pylint: disable=C0103


@register.simple_tag
def resize(image, width=None, height=None, crop=False, namespace="resized"):
    """
    Returns the url of the resized image
    """
    return resize_lazy(image=image, width=width, height=height, crop=crop,
                       namespace=namespace, as_url=True)


# pylint: disable=R0913
@register.simple_tag
def conditional_resize(image, ratio, width=None, height=None, upcrop=True,
                       namespace="resized"):
    """
    Crop the image based on a ratio

    If upcrop is true, crops the images that have a higher ratio than the given
    ratio, if false crops the images that have a lower ratio
    """
    aspect = float(image.width) / float(image.height)
    crop = False

    if (aspect > ratio and upcrop) or (aspect <= ratio and not upcrop):
        crop = True

    return resize_lazy(image=image, width=width, height=height, crop=crop,
                       namespace=namespace, as_url=True)
# pylint: enable=R0913
