from typing import Any

from django import template

register = template.Library()


@register.filter(name="get_item")
def get(item: Any, string: str) -> Any:
    """Return value at item[string]."""
    return item.get(string, "")
