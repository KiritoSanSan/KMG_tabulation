from django.urls import path
from .views import *

urlpatterns = [
    path('tabel_admin',tabel_admin,name='tabel_admin'),
    path('tabel_admin_update', tabel_admin_update, name='tabel_admin_update'),
    path('tabel_approved_admin',tabel_approved_admin,name='tabel_approved_admin'),
]
