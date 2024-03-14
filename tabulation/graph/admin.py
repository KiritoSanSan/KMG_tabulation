from django.contrib import admin
from .models import *
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode
# Register your models here.


    
@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('name','description')

@admin.register(Attendance)
class AttendenceAdmin(admin.ModelAdmin):
    list_display = ('type','name','description')

class EmployeesInline(admin.TabularInline):
    model = Graph.employees.through
    extra = 1

    

@admin.register(Employees)
class EmployeesAdmin(admin.ModelAdmin):
    list_display = ('tabel_number',
                    'name',
                    'surname',
                    'middlename',
                    'job',
                    'oil_place')

@admin.register(Graph)
class GraphAdmin(admin.ModelAdmin):
    inlines = [EmployeesInline]
    list_display = ('id',
                    'reservoir',
                    'subdivision',
                    'month',
                    'year',
                    'view_graph_link',
                    # 'view_tabel_link',
                    )
    list_filter = ('reservoir',
                   'year',
                   'subdivision')
    #Add link to check each graph by pk
    def view_graph_link(self,obj):
         graph = obj.pk
         url = (
              reverse("graph:graph_admin")
                      +"?"
                      +urlencode({'graph_pk':graph})
         )
         return format_html('<a href={}>{}',url,f"График {graph}" )
    view_graph_link.short_description = 'Графики'

    # def view_tabel_link(self, obj):
    #     filters = {
    #         'reservoir': obj.reservoir,
    #         'subdivision': obj.subdivision,
    #         'month': obj.month,
    #         'year': obj.year
    #     }
    #     url = (
    #         reverse("tabel:filtered_tabel_graph")
    #         + "?"
    #         + urlencode(filters)
    #     )
    #     return format_html('<a href={}>{}', url, f"Табель {obj.pk}")
    # view_tabel_link.short_description = 'Табели'
         




@admin.register(OilPlace)
class OilPlaceAdmin(admin.ModelAdmin):
    list_display = ('name','description')


@admin.register(Subdivision)
class SubdivisionAdmin(admin.ModelAdmin):
    list_display = ('name','description')

@admin.register(TimeTracking)
class TimeTrackingAdmin(admin.ModelAdmin):
        list_display = ('employee_id',
                    'date',
                    'worked_hours',
                    )

