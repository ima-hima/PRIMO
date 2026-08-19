from django import template
from django.templatetags.static import static

register = template.Library()


@register.simple_tag
def react_asset(entry: str) -> str:
    """Return the static URL for a Vite-built React asset."""
    return static(f"primo/react/{entry}")
