
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(('users.urls', 'users'), namespace='users')),
    path('',include(('graph.urls','graph'),namespace='graph')),
    path('',include(('tabel.urls','tabel'),namespace='tabel')),
]
