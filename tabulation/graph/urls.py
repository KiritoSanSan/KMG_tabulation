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
]
