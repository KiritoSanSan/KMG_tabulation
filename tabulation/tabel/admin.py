from django.contrib import admin
from .models import *
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode
# Register your models here.

#Employee Inline
class EmployeesInline(admin.TabularInline):
    model = Tabel.employees.through

    #sey ReadOnly on Inline
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = [field.name for field in self.model._meta.get_fields()]
        return readonly_fields
    
    #remove the button 'add employee'
    def has_add_permission(self, request, obj=None):
            return False
    

@admin.register(Tabel)
class AdminTabel(admin.ModelAdmin):
    inlines = [EmployeesInline]
    list_display = ('id',
                    'reservoir',
                    'subdivision',
                    'month',
                    'year',
                    )
    list_filter = ('reservoir',
                   'year',
                   'subdivision')


