"""
Custom template tags for the tracemap module
"""
import os

from django import template


register = template.Library()


def relpath(path, relative_to):
    """
    Return a path the input path to a given directory
    Args:
        path:
        relative_to:

    Returns:

    """
    if path is not None:
        return os.path.relpath(path, relative_to)

    return None


register.filter('relpath', relpath)


def dict_key(source_dict: dict, key_name):
    """
    Extract a single key
    Args:
        source_dict:
        key_name:

    Returns:

    """
    return source_dict.get(key_name)


register.filter('dict_key', dict_key)


def blank_none(value):
    """
    Return a blank string if input parameter is None
    Args:
        value:

    Returns:

    """
    return value if value is not None else ''


register.filter('blank_none', blank_none)
