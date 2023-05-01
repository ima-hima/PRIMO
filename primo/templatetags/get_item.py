from django import template

register = template.Library()


@register.filter(name="get_item")
def get(item, string):
    """Return value at item[string]."""
    return item.get(string,'')
