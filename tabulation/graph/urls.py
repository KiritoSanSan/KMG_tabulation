from django.urls import path
from .views import *

urlpatterns = [
    path('',home,name='home'),
    path('graph-admin/',graph_admin,name='graph_admin')
]
