from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    return value * arg

@register.filter
def sum(cart_items):
    return sum(item.quantity * item.product.unit_price for item in cart_items)
