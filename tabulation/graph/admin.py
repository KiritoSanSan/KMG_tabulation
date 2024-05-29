from typing import Any
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.admin.sites import site
from django.db.models.base import Model
from django.http import HttpResponse
from .models import *
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode
from django.contrib.admin.views.main import ChangeList
from django.contrib.admin.utils import quote

# Register your models here.

    

admin.autodiscover()
# admin.site.enable_nav_sidebar = False

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('name','description')

@admin.register(Attendance)
class AttendenceAdmin(admin.ModelAdmin):
    list_display = ('type','name','description')

@admin.register(Employees)
class EmployeesAdmin(admin.ModelAdmin):
    list_display = ('tabel_number',
                    'name',
                    'surname',
                    'middlename',
                    'job',
                    'oil_place')

# class ChangeLink(ChangeList):
#      def url_for_result(self, result: Model) -> str:
#         pk = getattr(result,self.pk_attname)
#         return '/foos/foo/%d/' % (quote(pk))

@admin.register(Graph)
class GraphAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'reservoir',
                    'subdivision',
                    'month',
                    'year',
                    'view_graph_link',
                    'status',
                    # 'parsing_graph',
                    )
    list_filter = ('reservoir',
                   'year',
                   'subdivision')
    readonly_fields = ('status',)

    #Add link to check each graph by pk
    def view_graph_link(self,obj):
        graph = obj.pk
        url = (
            reverse("graph:graph_admin")
                    +"?"
                    +urlencode({'graph_pk':graph})
        )
        return format_html('<a href={}>{}',url,f"График Вахты №{graph}")
    view_graph_link.short_description = 'Графики'
    def parsing_graph(self,obj):
        url = (reverse('graph:graph_parsing'))
        return format_html('<a href={}>{}',url,'Парсинг Excel Графиков')
    parsing_graph.short_description = 'Парсинг Графиков'

    # def get_readonly_fields(self, request, obj=None):
    #         readonly_fields = list(super().get_readonly_fields(request, obj))
    #         if obj:
    #             readonly_fields.append('status')
    #         return readonly_fields




@admin.register(OilPlace)
class OilPlaceAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Subdivision)
class SubdivisionAdmin(admin.ModelAdmin):
    list_display = ('name',)

# class TimeTrackingEmployeeInline(admin.TabularInline):
#      model = TimeTracking.employee_id.through
#      extra = 1

@admin.register(TimeTracking)
class TimeTrackingAdmin(admin.ModelAdmin):
        list_display = (
                    'employee_id',
                    'worked_hours',
                    'date',
                    )

# @admin.register(GraphEmployeesList)
# class GraphEmployeesListAdmin(admin.ModelAdmin):
#     list_display = ('employee_id', 'graph_id')
        




