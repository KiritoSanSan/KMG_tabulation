from django.contrib import admin
from .models import *

admin.site.register(Employees)
admin.site.register(Job)
admin.site.register(Subdivision)
admin.site.register(OilPlace)
admin.site.register(Attendance)
admin.site.register(TimeTracking)
admin.site.register(WorkedTime)