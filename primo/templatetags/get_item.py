from django import template

register = template.Library()


@register.filter(name="get_item")
def get(item, string):
    print(item)
    print(string)
    return item.get(string,'')
