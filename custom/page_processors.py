# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.template.defaultfilters import slugify

from mezzanine.conf import settings
from mezzanine.pages.page_processors import processor_for
from mezzanine.utils.views import paginate

from cartridge.shop.models import Category, Product, ProductOption, ProductVariation
from django.db.models import CharField, Q
from decimal import Decimal
from functools import reduce
from operator import iand, ior
from copy import deepcopy


@processor_for(Category)
def category_processor(request, page):
    """
    Add paging/sorting to the products for the category.
    """

    # my code
    """
    GET = {}
    args=os.getenv("QUERY_STRING").split('&')
    for arg in args:
        t = arg.split('=')
        if len(t)>1: k,v=arg.split('='); GET[k.lower()]=t
    """
    GET = {}  # GET dict
    options_types = {}  # A dict for options menu header title
    options_all = {}  # All options dict
    querystring = ""  # Query string

    if request.GET.get("sort"): GET["sort"] = ("sort=%s" % request.GET.get("sort"))
    if request.GET.get("page"): GET["page"] = ("page=%s" % request.GET.get("page"))

    # Initialize by request.GET 'GET' and 'options_get_split[type_name]' with split list of GET values or None
    options_get_split = {}
    for type_name in [unicode(option[1]).lower() for option in settings.SHOP_OPTION_TYPE_CHOICES]:
        if request.GET.get(type_name):
            options_get_split[type_name] = request.GET.get(type_name).split('|')
            GET[type_name] = "%s=%s" % (type_name, request.GET.get(type_name))
        else:
            options_get_split[type_name] = []
            GET[type_name] = []

    # Form querystring excluding key 'sort'
    querylist = [GET[item] for item in GET if GET[item] and item != "sort"]
    if querylist: querystring = '&%s' % '&'.join(querylist)

    # Read dict of 'options_all' and set all items to 'checked' or 'not checked' comparing with 'options_get'
    for option in ProductOption.objects.all():
        # some vars
        option_type_display = option.get_type_display()
        checked = option.name in options_get_split.get(option_type_display.lower())

        # copy new dicts & lists for url buiding
        options_get_split_list = list(options_get_split.get(option_type_display.lower()))
        GET_copy = dict(GET)

        del GET_copy[option_type_display.lower()]
        # if there is any get options for current
        if checked:
            options_get_split_list.remove(option.name)
        else: # add to url
            options_get_split_list.append(option.name)
        
        GET_copy[option_type_display.lower()] = []
        if options_get_split_list:
            GET_copy[option_type_display.lower()] = "%s=%s" % (option_type_display.lower(), "|".join(options_get_split_list))
                   

        # we form option_url
        option_url = "&".join([GET_copy[item] for item in GET_copy if GET_copy[item]])
        if option_url:
            option_url = "?%s" % option_url

        # update 'option1' and 'option2' with 'option_type_display'
        options_types.update({"option%s" % option.type: option_type_display})
        options_all.setdefault("option%s" % option.type, [])\
           .append({"option_type": option_type_display, "option_name": option.name,
                    "checked": checked, "option_url": request.path + option_url})

    # Filters by default from page.category.filters
    #filters = [page.category.filters()]

    # User 'options_filters'
    options_filters = []
    lookup = {}
    for option in options_all:
        for item in options_all.get(option):
            if item["checked"]:
                lookup.setdefault("%s__in" % option, []).append(item["option_name"])
    options_filters.append(Q(**lookup))

    if options_filters:
        options_filters = reduce(iand, options_filters)
        variations = ProductVariation.objects.filter(options_filters)
        options_filters = [Q(variations__in=variations)]
        options_filters = reduce(iand, options_filters)
        #filters.append(options_filters)
    
    #filters = reduce(iand, filters)
    ####################### 

    settings.use_editable()
    products = Product.objects.published(for_user=request.user)\
                        .filter(options_filters).distinct()
                        #).filter(options_filters).filter(page.category.filters()).distinct()
    sort_options = [(slugify(option[0]), option[1])
                    for option in settings.SHOP_PRODUCT_SORT_OPTIONS]
    sort_by = request.GET.get("sort", sort_options[0][1])
    products = paginate(products.order_by(sort_by),
                        request.GET.get("page", 1),
                        settings.SHOP_PER_PAGE_CATEGORY,
                        settings.MAX_PAGING_LINKS)
    products.sort_by = sort_by
    sub_categories = page.category.children.published()
    child_categories = Category.objects.filter(id__in=sub_categories)
    
    return {"products": products, "child_categories": child_categories,
            "options_all": options_all,
            "options_types": options_types,
            "querystring": querystring,
           }
