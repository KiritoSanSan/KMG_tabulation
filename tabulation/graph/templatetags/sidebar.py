from django.template import Library
from graph.models import *
from django.utils.text import capfirst

from django.contrib.admin import AdminSite
from django.contrib import admin 
register = Library()

@register.inclusion_tag('graph/sidebar.html')
def sidebar_view(request):
    pass