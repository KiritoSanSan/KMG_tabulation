from django.contrib import admin
from .models import *
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode
# Register your models here.

#Employee Inline
class EmployeesInline(admin.TabularInline):
    model = Tabel.employees.through

    #set ReadOnly to Inline
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = [field.name for field in self.model._meta.get_fields()]
        return readonly_fields
    
    #remove the button 'add employee'
    def has_add_permission(self, request, obj=None):
        return False
    
    #remove the button 'remove employee'
    def has_delete_permission(self, request, obj=None):
        return False
    


@admin.register(Tabel)
class AdminTabel(admin.ModelAdmin):
    readonly_fields = ('id',
                    'reservoir',
                    'subdivision',
                    'month',
                    'year',
                    )
    list_display = ('id',
                    'reservoir',
                    'subdivision',
                    'month',
                    'year',
                    'view_tabel_link',
                    )
    list_filter = ('reservoir',
                   'year',
                   'subdivision')
    
    def view_tabel_link(self,obj):
         tabel = obj.pk
         url = (
              reverse("tabel:tabel_admin")
                      +"?"
                      +urlencode({'tabel_pk':tabel})
         )
         return format_html('<a href={}>{}',url,f"Согласованный Табель {tabel}" )
    view_tabel_link.short_description = 'Согласованные Табеля'

# @admin.register(TimeTrackingTabel)
# class TimeTrackingTabelAdmin(admin.ModelAdmin):
#     list_display = ('employee_id', 'worked_hours', 'date')

# @admin.register(TabelApprovedTimeTracking)
# class AdminTabelApprovedTimeTracking(admin.ModelAdmin):
#     list_display = ('employee_id', 'worked_hours', 'date')

@admin.register(TabelApproved)
class AdminTabelApproved(admin.ModelAdmin):
    readonly_fields = ('id',
                    'reservoir',
                    'subdivision',
                    'month',
                    'year',
                    )
    list_display = ('id',
                    'reservoir',
                    'subdivision',
                    'month',
                    'year',
                    'view_tabel_link',
                    )
    list_filter = ('reservoir',
                   'year',
                   'subdivision')
    

    def view_tabel_link(self,obj):
         tabel = obj.pk
         url = (
              reverse("tabel:tabel_approved_admin")
                      +"?"
                      +urlencode({'tabel_pk':tabel})
         )
         return format_html('<a href={}>{}',url,f"Утвержденный Табель {tabel}" )
    view_tabel_link.short_description = 'Утвержденные Табеля'