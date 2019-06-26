import os

from django import template


register = template.Library()


def relpath(path, relative_to):
    if path is not None:
        return os.path.relpath(path, relative_to)
    else:
        return None


register.filter('relpath', relpath)


def dict_key(d: dict, k):
    return d.get(k)


register.filter('dict_key', dict_key)


def blank_none(v):
    return v if v is not None else ''


register.filter('blank_none', blank_none)
