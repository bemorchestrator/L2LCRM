# menu/templatetags/menu_tags.py

from django import template
from menu.models import Menu
from django.contrib.auth.models import Group

register = template.Library()

def filter_items(items, user_groups):
    filtered_items = []
    for item in items:
        include_item = True  # Temporarily include all items
        if include_item:
            # Recursively filter children
            children = filter_items(item.children.all(), user_groups)
            filtered_items.append({
                'item': item,
                'children': children
            })
    return filtered_items



@register.inclusion_tag('menu/menu_template.html', takes_context=True)
def load_menu(context):
    request = context['request']
    user = request.user
    if user.is_authenticated:
        user_groups = user.groups.values_list('id', flat=True)
    else:
        user_groups = []

    menus = Menu.objects.prefetch_related('items__children').all()
    filtered_menus = []
    for menu in menus:
        top_level_items = menu.items.filter(parent=None)
        filtered_items = filter_items(top_level_items, user_groups)
        if filtered_items:
            filtered_menus.append({
                'menu': menu,
                'items': filtered_items
            })
    # Debug output
    return {'menus': filtered_menus}