from django.urls import path
from django.contrib import admin
from .views import *
from django.views.generic.base import RedirectView

# admin.autodiscover()
urlpatterns = [
    path('',home,name='home'),
    path('graph_admin',graph_admin,name='graph_admin'),
    path('graph_admin_update',graph_admin_update,name='graph_admin_update'),
    # path('', RedirectView.as_view(url='/admin/', permanent=True))
    # path('creation_timetracking',CreationTimeTracking.as_view(),name='creation_timetracking'),
    path('parsing_graph',upload_file,name='graph_parsing')
]
