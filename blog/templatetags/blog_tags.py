from django import template

register = template.Library()


@register.inclusion_tag('blog/_entry_history.html')
def entry_history():
    return {}
