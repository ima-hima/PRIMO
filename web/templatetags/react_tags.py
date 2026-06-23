import json
import os

from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def react_asset(entry: str) -> str:
    """Return the URL for a React bundle entry using asset-manifest.json."""
    manifest_path = os.path.join(
        settings.STATIC_ROOT, "primo", "react", "asset-manifest.json"
    )
    try:
        with open(manifest_path) as f:
            manifest = json.load(f)
        # Manifest paths are absolute (e.g. /static/primo/react/static/js/main.hash.js)
        # because we set PUBLIC_URL=/static/primo/react at build time.
        return manifest["files"][entry]
    except (FileNotFoundError, KeyError):
        return ""
