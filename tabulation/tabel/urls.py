from django.urls import path
from .views import *

urlpatterns = [
    path('tabel_admin',tabel_admin,name='tabel_admin'),
]
