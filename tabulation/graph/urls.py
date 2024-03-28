from django.urls import path
from django.contrib import admin
from .views import *
# admin.autodiscover()
urlpatterns = [
    path('',home,name='home'),
    path('graph-admin/',wrap_admin_view(graph_admin),name='graph_admin'),
    path('graph_admin_update',graph_admin_update,name='graph_admin_update'),
    # path('creation_timetracking',CreationTimeTracking.as_view(),name='creation_timetracking'),
    path('add_employee',add_employee,name='add_employee')
]
