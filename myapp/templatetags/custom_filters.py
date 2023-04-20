from django import template

register = template.Library()

@register.filter
def messageErreursExcell(messages, tag):
    return [m for m in messages if tag in m.tags]
