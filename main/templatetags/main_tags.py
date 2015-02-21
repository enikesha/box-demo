from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def menu_active(context, url, exact=False):
    path = context['request'].path
    active = path.startswith(url) if not exact else url == path
    return ' class="active"' if active else ''
