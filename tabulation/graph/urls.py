from django.urls import path
from .views import *

urlpatterns = [
    path('',home,name='home'),
    path('graph_admin/',graph_admin,name='graph_admin'),
    path('graph_admin_update',graph_admin_update,name='graph_admin_update'),
]
