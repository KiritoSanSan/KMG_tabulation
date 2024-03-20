from django.template import Library
from graph.models import *
register = Library()

@register.inclusion_tag('graph/sidebar.html')
def sidebar_view():
    graph = Graph.objects.all()
