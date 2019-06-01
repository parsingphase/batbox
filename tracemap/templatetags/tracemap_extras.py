from django import template
import os

register = template.Library()


def relpath(path, relative_to):
    if path is not None:
        return os.path.relpath(path, relative_to)
    else:
        return None


register.filter('relpath', relpath)
