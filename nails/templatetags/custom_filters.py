from django import template

register = template.Library()


@register.filter
def currency_vnd(value):
    try:
        value = float(value)
        return "{:,.0f} ₫".format(value)
    except (ValueError, TypeError):
        return value
