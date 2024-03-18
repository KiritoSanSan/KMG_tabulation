from django.urls import path
from django.contrib import admin
from .views import *
# admin.autodiscover()
urlpatterns = [
    path('',home,name='home'),
    path('graph-admin/',graph_admin,name='graph_admin'),
    path('graph_admin_update',graph_admin_update,name='graph_admin_update'),
]
