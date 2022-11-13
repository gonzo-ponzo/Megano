from django import template
register = template.Library()


@register.filter
def index(list_of_values, i):
    return list_of_values[int(i): int(i)+1]
