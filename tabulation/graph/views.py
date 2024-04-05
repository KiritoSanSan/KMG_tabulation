import calendar
import json
from django.urls import NoReverseMatch
from django.utils.text import capfirst

from functools import update_wrapper
from typing import Any
from django.apps import apps

from django.db.models.query import QuerySet
from django.views.generic import ListView, CreateView, FormView, DetailView
from datetime import datetime
from django.contrib.admin import AdminSite
from django.contrib import admin 
from django.contrib.admin.sites import site
from django.shortcuts import get_object_or_404, redirect, render
from .models import *
from django.db.models import Q
from django.contrib.admin.options import ModelAdmin

from django.contrib.admin.utils import flatten_fieldsets

from django.contrib.admin.helpers import AdminForm, InlineAdminFormSet

from django.contrib.admin.options import get_content_type_for_model
from django.contrib import messages
from tabel.models import Tabel
from .forms import *
from django.core.exceptions import ObjectDoesNotExist
from tabel.models import TimeTrackingTabel

# Create your views here.

YEARS_CHOICES = (
    ('2023','2023'),
    ('2024','2024'),
    ('2025','2025')
)

month_names_ru = {
    "January": "Январь",
    "February": "Февраль",
    "March": "Март",
    "April": "Апрель",
    "May": "Май",
    "June": "Июнь",
    "July": "Июль",
    "August": "Август",
    "September": "Сентябрь",
    "October": "Октябрь",
    "November": "Ноябрь",
    "December": "Декабрь"
}

#filter checking valid or not
def is_valid_queryparam(param):
    return param != '---' and param is not None

#show sidebar
def sidebar(request):
    admin_site = AdminSite()
    available_apps = []

    app_list = admin.site.get_app_list(request)
    for app in app_list:
        app_name = app['name']
        app_label = app['app_label']
        app_url = reverse('admin:index') + f"{app_label}/"
        models_list = []
        for model_dict in app['models']:
            model = model_dict.get('model')  # Get the model class if it exists
            model_admin = admin_site._registry.get(model)
            # print(model_admin)
            if model:
                app_label = model._meta.app_label

                # has_module_perms = model_admin.has_module_permission(request)
                # if not has_module_perms:
                #     continue

                # perms = model_admin.get_model_perms(request)
                # print("perms",perms)
                # if True not in perms.values():
                #     continue

                info = (app_label, model._meta.model_name)
                model_info = {
                    "model": model,
                    "name": capfirst(model._meta.verbose_name_plural),
                    "object_name": model._meta.object_name,
                    # "perms": perms,
                    "admin_url": None,
                    "add_url": None,
                }
                model_info["admin_url"] = reverse(
                            "admin:%s_%s_changelist" % info, current_app=capfirst(model._meta.verbose_name_plural)
                        )
                model_info["add_url"] = reverse(
                            "admin:%s_%s_add" % info, current_app=capfirst(model._meta.verbose_name_plural)
                        )
                # if perms.get("change") or perms.get("view"):
                #     model_info["view_only"] = not perms.get("change")
                #     try:
                #         model_info["admin_url"] = reverse(
                #             "admin:%s_%s_changelist" % info, current_app=capfirst(model._meta.verbose_name_plural)
                #         )
                #     except NoReverseMatch:
                #         pass
                # if perms.get("add"):
                #     try:
                #         model_info["add_url"] = reverse(
                #             "admin:%s_%s_add" % info, current_app=capfirst(model._meta.verbose_name_plural)
                #         )
                #     except NoReverseMatch:
                #         pass
                # print("MODEL info",model_info)
                models_list.append(model_info)
        available_apps.append(
            {
                'name': app_name,
                'models': models_list,
                'app_label': app_label,
                'app_url': app_url
            }
        )

    data = {
        "has_permission": True,
        "available_apps": available_apps,
        "site_title": admin_site.site_title,
        "site_header": admin_site.site_header,
    }

    admin_context = admin_site.each_context(request)
    admin_context.update(data)
    return admin_context

def home(request):
    graph =  Graph.objects.all()
    reservoir_form = GraphReservoirForm()
    subdivision_form = GraphSubdivisionForm()
    years = YearSelectForm()

    #filters start

    filter_year = request.GET.get('years')
    request.session['selected_year'] = filter_year

    filter_reservoir = request.GET.get('mesto')
    request.session['selected_reservoir'] = filter_reservoir

    filter_subdiv = request.GET.get('podrazd')
    request.session['selected_subdivision'] = filter_subdiv


    if is_valid_queryparam(filter_year):
        graph = graph.filter(year=filter_year)

    if is_valid_queryparam(filter_reservoir):
        graph = graph.filter(reservoir__name__icontains=filter_reservoir)

    if is_valid_queryparam(filter_subdiv):
        graph = graph.filter(subdivision__name__icontains=filter_subdiv)

    #filters end
        
    context = {
        'selected_year':request.session['selected_year'],
        "selected_reservoir": request.session['selected_reservoir'],
        "selected_subdivision": request.session['selected_subdivision'],        
        'graph':graph,
        'year_form':years,
        "reservoir":reservoir_form,
        "subdivision":subdivision_form,
    }
    return render(request,'graph/home.html',context)


def wrap_admin_view(view, cacheable=False):
    """
    Use this to wrap view functions used in admin dashboard
    Note: Only the views that require a admin login
    """
    from django.contrib import admin

    def wrapper(*args, **kwargs):
        return admin.site.admin_view(view, cacheable)(*args, **kwargs)

    wrapper.admin_site = admin.site
    return update_wrapper(wrapper, view)


def graph_admin(request):
    #chosen graph
    if 'graph_pk' in request.GET:
        graph_pk = request.GET['graph_pk']
        request.session['chosen_pk'] = graph_pk
        
    #soglasovat' graphik
    if request.method == 'POST':
        # Check if the submitted form contains the key 'approve_graph'
        if 'approve_graph' in request.POST:
            graph_pk = request.POST.get('graph_pk')
            graph_inst = Graph.objects.get(pk=graph_pk)
            # Create a Tabel instance with data from the chosen graph
            employees_graph = graph_inst.employees.all()
            try:
                # Attempt to retrieve an existing Tabel instance
                tabel_instance = Tabel.objects.get(
                    reservoir=graph_inst.reservoir,
                    subdivision=graph_inst.subdivision,
                    month=graph_inst.month,
                    year=graph_inst.year,
                )
                if tabel_instance:
                    messages.error(request,'Табель уже согласован')
            except ObjectDoesNotExist:
                # If Tabel object doesn't exist, create it
                tabel_instance = Tabel.objects.create(
                    reservoir=graph_inst.reservoir,
                    subdivision=graph_inst.subdivision,
                    month=graph_inst.month,
                    year=graph_inst.year,
                )

                for employee in employees_graph:
                    time_tracking = TimeTracking.objects.filter(employee_id=employee).values()
                    employee_instance = Employees.objects.get(pk=employee.tabel_number)
                    for value in time_tracking:
                        TimeTrackingTabel.objects.create(
                            employee_id = employee_instance,
                            date = value['date'],
                            worked_hours = value['worked_hours']
                        )
                # Set the many-to-many relationship using the .set() method
                tabel_instance.employees.set(employees_graph)
                messages.success(request,'Табель согласован')
                return redirect('admin:tabel_tabel_changelist')

    graph_pk = request.session['chosen_pk']  
    graph = Graph.objects.get(pk=graph_pk)
    employees = graph.employees.all()
    attendance = Attendance.objects.filter(type='дни явок')
    no_attendance = Attendance.objects.filter(type='дни неявок')
    tracking = TimeTracking.objects.all()
    month = graph.month
    year = graph.year


    name_month_en = calendar.month_name[int(month)]
    name_month_ru = month_names_ru[name_month_en]

    if month and month is not None:
        filter_month = int(month)
        tracking = TimeTracking.objects.filter(employee_id__in = employees.values_list('tabel_number',flat=True))
        tracking = tracking.filter(date__month=filter_month)
        tabel_numbers = tracking.values_list('employee_id',flat=True)
        employees = employees.filter(tabel_number__in=tabel_numbers)

    if year and year is not None:
        filter_year = int(year)
        tracking = TimeTracking.objects.filter(employee_id__in = employees.values_list('tabel_number',flat=True))
        tracking = tracking.filter(date__year=filter_year)
        tabel_numbers = tracking.values_list('employee_id',flat=True)
        employees = employees.filter(tabel_number__in=tabel_numbers)


    tracking = tracking.filter(date__year=int(year)).filter(date__month=int(month))
    dates = tracking.values_list('date',flat=True).distinct()

    for date in dates:
        month = date.month
        year = date.year
    num_days = calendar.monthrange(int(year),int(month))[1]
    days = range(1,num_days+1)

    #attendace calculation start
    directory = {}
    for employee in employees:
        pairs = [('worked_days', 0), ('weekends', 0), ('days_in_month', len(days)), ('total_work_hours', 0)]
        directory[f'{employee.name}'] = dict(pairs)

    for employee in employees:
        for work in tracking:
            if work.employee_id == employee:
                if str(work.worked_hours).isdigit():
                    directory[f'{employee.name}']['worked_days'] += 1 
                    directory[f'{employee.name}']['total_work_hours'] += int(work.worked_hours)
                else:
                    directory[f'{employee.name}']['weekends'] += 1

    #attendance calculation end

    context = {
        'graph_pk':graph_pk,
        "year":year,
        "month":month,
        'days':days,
        "selected_month": name_month_ru,
        'employees':employees,
        'attendance': attendance, 
        'no_attendance': no_attendance,
        'time_tracking': tracking,
        'graph':graph,
        'calculations': directory,
    }
    #adding admin side bar start
    context.update(sidebar(request))
    return render(request,'graph/graph_admin.html',context)

def graph_admin_update(request):
    search_text = request.POST.get('time_tracking_set-prefix-employee_id')
    graph_pk = request.session['chosen_pk']
    graph = Graph.objects.get(pk=graph_pk)
    employees = graph.employees.all()
    attendance_all = Attendance.objects.all()
    attendance = Attendance.objects.filter(type="дни явок")
    no_attendance = Attendance.objects.filter(type="дни неявок")
    tracking = TimeTracking.objects.all()
    month = int(graph.month)
    year = int(graph.year)
    
    try:
        search_employee = Employees.objects.filter(
            Q(tabel_number__icontains=search_text) |
            Q(name__icontains=search_text)| 
            Q(surname__icontains=search_text) | 
            Q(middlename__icontains=search_text)).exclude(
            tabel_number__in=employees.values_list('tabel_number', flat=True)
            )
    except:
        search_employee = Employees.objects.filter().exclude(
            tabel_number__in=employees.values_list('tabel_number', flat=True)
        )

    if month and month is not None:
        filter_month = int(month)
        tracking = TimeTracking.objects.filter(employee_id__in = employees.values_list('tabel_number',flat=True))
        tracking = tracking.filter(date__month=filter_month)
        tabel_numbers = tracking.values_list('employee_id',flat=True)
        employees = employees.filter(tabel_number__in=tabel_numbers)
    if year and year is not None:
        filter_year = int(year)
        tracking = TimeTracking.objects.filter(employee_id__in = employees.values_list('tabel_number',flat=True))
        tracking = tracking.filter(date__year=filter_year)
        tabel_numbers = tracking.values_list('employee_id',flat=True)
        employees = employees.filter(tabel_number__in=tabel_numbers)
    
    
    dates = tracking.values_list('date',flat=True).distinct()
    for date in dates:
        month = date.month
        year = date.year
    num_days = calendar.monthrange(int(year),int(month))[1]
    days = range(1,num_days+1)
    # print(request.body.decode('utf-8'))

    if request.method == 'POST':
        if request.headers["content-type"].strip().startswith("application/json"):
            if "employee_id_delete" in request.body.decode('utf-8'):
                employee_deletion_data = json.loads(request.body)
                employee_tabel_number = employee_deletion_data.get('employee_id_delete')
                empl = Employees.objects.get(pk=employee_tabel_number)
                # print(empl)
                # print(employee_tabel_number)
                graph.employees.remove(empl)
                TimeTracking.objects.filter(employee_id = employee_tabel_number).delete()
                    
            if "employee_id" in request.body.decode('utf-8'):
                employee_addition_data = json.loads(request.body)
                employee_tabel_number = employee_addition_data.get('employee_id')
                empl = Employees.objects.get(pk=employee_tabel_number)
                for day in days:
                    TimeTracking.objects.create(
                        employee_id = empl,
                        date = datetime.datetime(year, month, day),
                        worked_hours = ''
                    )
                graph.employees.add(employee_tabel_number)


        for key, value in request.POST.items():
            # print(request.POST)
            if key.startswith('worked_hours_'):
                time_tracking_day = int(key.split('_')[4])  
                key_parts = key.split('_')
                if len(key_parts) > 5:
                    for day in days:
                        time_tracking_employee = key.split('_')[4] + "_" + key.split('_')[5]
                        if day == time_tracking_day:
                                time_tracking_id = key.split('_')[3]
                                time_tracking_instance = TimeTracking.objects.get(pk=time_tracking_id)
                                time_tracking_instance.worked_hours = value
                                time_tracking_instance.save()
                        else:
                            TimeTracking.objects.create(
                                employee_id=time_tracking_employee,
                                date=datetime(int(year), int(month), day),
                                worked_hours="0",
                            )
                else:
                    time_tracking_id = key.split('_')[3]
                    time_tracking_instance = TimeTracking.objects.get(pk=time_tracking_id)
                    time_tracking_instance.worked_hours = value
                    time_tracking_instance.save()

        return redirect(reverse('graph:graph_admin') +f'?graph_pk={graph_pk}')
    
    name_month_en = calendar.month_name[int(month)]
    name_month_ru = month_names_ru[name_month_en]
    
    tracking = tracking.filter(date__year=int(year)).filter(date__month=int(month))

    #attendance calculation start
    directory = {}
    for employee in employees:
        pairs = [('worked_days', 0), ('weekends', 0), ('days_in_month', len(days)), ('total_work_hours', 0)]
        directory[f'{employee.name}'] = dict(pairs)

    for employee in employees:
        for work in tracking:
            if work.employee_id == employee:
                if str(work.worked_hours).isdigit():
                    directory[f'{employee.name}']['worked_days'] += 1 
                    directory[f'{employee.name}']['total_work_hours'] += int(work.worked_hours)
                else:
                    directory[f'{employee.name}']['weekends'] += 1
    
    #attendance calculation end
    
    employee_form = EmployeeCreateForm()
    context = {
        'employees_all': search_employee,
        'graph_pk':graph_pk,
        "year":year,
        "month":month,
        'days':days,
        "selected_month": name_month_ru,
        'employees':employees,
        'attendance': attendance, 
        'attendance_all': attendance_all,
        'no_attendance': no_attendance,
        'time_tracking': tracking,
        'graph':graph,
        'calculations': directory,
    }
    context.update(sidebar(request))

    return render(request,'graph/graph_admin_update.html',context)










