# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from future.builtins import str

from decimal import Decimal
import locale
import platform

from django import template

from cartridge.shop.utils import set_locale

# my shop_tags
from cartridge.shop.models import Category, Product
# /my shop_tags

register = template.Library()


@register.filter
def currency(value):
    """
    Format a value as currency according to locale.
    """
    set_locale()
    if not value:
        value = 0
    value = '{0:.2f}'.format(float(value)) + u" грн."
    return value


def _order_totals(context):
    """
    Add shipping/tax/discount/order types and totals to the template
    context. Use the context's completed order object for email
    receipts, or the cart object for checkout.
    """
    fields = ["shipping_type", "shipping_total", "discount_total",
              "tax_type", "tax_total"]
    if "order" in context:
        for field in fields + ["item_total"]:
            context[field] = getattr(context["order"], field)
    else:
        context["item_total"] = context["request"].cart.total_price()
        if context["item_total"] == 0:
            # Ignore session if cart has no items, as cart may have
            # expired sooner than the session.
            context["tax_total"] = 0
            context["discount_total"] = 0
            context["shipping_total"] = 0
        else:
            for field in fields:
                context[field] = context["request"].session.get(field, None)
    context["order_total"] = context.get("item_total", None)
    if context.get("shipping_total", None) is not None:
        context["order_total"] += Decimal(str(context["shipping_total"]))
    if context.get("discount_total", None) is not None:
        context["order_total"] -= Decimal(str(context["discount_total"]))
    if context.get("tax_total", None) is not None:
        context["order_total"] += Decimal(str(context["tax_total"]))
    return context


@register.inclusion_tag("shop/includes/order_totals.html", takes_context=True)
def order_totals(context):
    """
    HTML version of order_totals.
    """
    return _order_totals(context)


@register.inclusion_tag("shop/includes/order_totals.txt", takes_context=True)
def order_totals_text(context):
    """
    Text version of order_totals.
    """
    return _order_totals(context)


@register.inclusion_tag("shop/includes/shop_latest.html")
def shop_latest(category, count):
    try:
        category = Category.objects.get(slug=category)
        products = Product.objects.filter(category.filters()).distinct().order_by('-rating')[0:count]
    except Category.DoesNotExist:
        products = []
    return {'products': products}

@register.inclusion_tag("shop/includes/option_items.html")
def option_items(option, options):
    return {'items': list(options.get(option))}

@register.assignment_tag
def get_item(dictionary, key):
    return dictionary.get(key)
