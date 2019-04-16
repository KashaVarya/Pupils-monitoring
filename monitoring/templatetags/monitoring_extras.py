import re

from django import template
from django.urls import reverse, NoReverseMatch

register = template.Library()


@register.simple_tag(takes_context=True)
def active(context, pattern_or_urlname):
    try:
        pattern = '^{}$'.format(reverse(pattern_or_urlname))
    except NoReverseMatch:
        pattern = pattern_or_urlname

    path = context['request'].path

    return 'active' if re.search(pattern, path) else ''
