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

from tabel.models import Tabel
from .forms import *
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from tabel.models import TimeTrackingTabel

# Create your views here.

YEARS_CHOICES = (
    ('2023','2023'),
    ('2024','2024'),
    ('2025','2025')
)
def russian_month_to_int(month):
    month_names = {
        'Январь': 1,
        'Февраль': 2,
        'Март': 3,
        'Апрель': 4,
        'Май': 5,
        'Июнь': 6,
        'Июль': 7,
        'Август': 8,
        'Сентябрь': 9,
        'Октябрь': 10,
        'Ноябрь': 11,
        'Декабрь': 12
    }
    # Convert month to title case to handle different capitalizations
    month_title = month.strip().title()
    return month_names.get(month_title, None)
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
    attendance_full = Attendance.objects.all()
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
        pairs = []
        pairs.append(('worked_days', 0))
        for att in attendance_full:
            pairs.append((f'{att}', 0))
        pairs.append(('total_work_hours', 0))
        directory[f'{employee.name}'] = dict(pairs)

    for employee in employees:
        for work in tracking:
            if work.employee_id == employee:
                if str(work.worked_hours).isdigit():
                    directory[f'{employee.name}']['worked_days'] += 1
                    directory[f'{employee.name}']['total_work_hours'] += int(work.worked_hours)
                for dir in directory[f'{employee.name}'].keys():
                    if dir == work.worked_hours:
                        directory[f'{employee.name}'][f'{dir}'] += 1

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
    attendance_full = Attendance.objects.all()
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
                time_tracking_day = int(key.split('_')[3])  
                key_parts = key.split('_')
                if len(key_parts) > 5:
                    for day in days:
                        time_tracking_employee = key.split('_')[4] + "_" + key.split('_')[5]
                        if day == time_tracking_day:
                                time_tracking_id = key.split('_')[2]
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
                    time_tracking_id = key.split('_')[2]
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
        pairs = []
        pairs.append(('worked_days', 0))
        for att in attendance_full:
            pairs.append((f'{att}', 0))
        pairs.append(('total_work_hours', 0))
        directory[f'{employee.name}'] = dict(pairs)

    for employee in employees:
        for work in tracking:
            if work.employee_id == employee:
                if str(work.worked_hours).isdigit():
                    directory[f'{employee.name}']['worked_days'] += 1
                    directory[f'{employee.name}']['total_work_hours'] += int(work.worked_hours)
                for dir in directory[f'{employee.name}'].keys():
                    if dir == work.worked_hours:
                        directory[f'{employee.name}'][f'{dir}'] += 1
    
    #attendance calculation end
    
    context = {
        'employees_all': search_employee,
        'graph_pk':graph_pk,
        "year":year,
        "month":month,
        'days':days,
        "selected_month": name_month_ru,
        'employees':employees,
        'attendance': attendance,
        'attendance_full':attendance_full, 
        'no_attendance': no_attendance,
        'time_tracking': tracking,
        'graph':graph,
        'calculations': directory,
    }
    
    #adding admin side bar start


    context.update(sidebar(request))

    
    #adding admin side bar end
    return render(request,'graph/graph_admin_update.html',context)

from openpyxl import load_workbook as lw

def upload_file(request):
    table_data = {
        'month': '',
        'data': [],
        'formatted': False
    }
    months = ['январь', 'февраль', 'март', 'апрель', 'май', 'июнь', 'июль', 'август', 'сентябрь', 'октябрь', 'ноябрь', 'декабрь']

    if request.method == 'POST' and request.FILES['file']:
        uploaded_file = request.FILES['file']
        # Do something with the uploaded file
        if uploaded_file.name.endswith('.xlsx'):
            load_workbook = lw(uploaded_file,data_only=True)
            graph = load_workbook.active

            data_length = 0
            while isinstance(graph['A' + str(5 + data_length)].value, int):
                data_length += 1
            # print(data_length)
            row_num = 4
            list_values = [str(x.value).lower() for x in graph['A']]
            list_values = list_values[3:]
            month = 1
            for j in range(1,len(months)+1):
                for value in list_values:
                    if any(month in value for month in months):
                        table_data['month'] = value.capitalize()
                        list_values = list_values[data_length+1:]
                        break
                for n in range(data_length+1):
                    row_num +=1
                    list = [x.value for x in graph[row_num]]
                    if list.count(None) > 3:
                        break
                    table_data['data'].append(list)


                #    
                for i in table_data['data']:
                    #adding job start
                    job_name = i[2].split(' ', 1)
                    if len(job_name) != 2:
                        job_name.append(' ')
                    elif job_name[0] == '':
                        job_name_temp = job_name[0].split(' ',1)
                        if len(job_name_temp) == 2:
                            job_name[0]=job_name_temp[0]
                            job_name[1]=job_name_temp[1]
                        else:
                            job_name[0]=job_name_temp[0]
                            job_name[1]=' '
                            # print('jobs ',job_name[0],job_name[1])
                    try:
                        job_instance = Job.objects.get(name=job_name[0])
                    except:
                        if job_name[0] != '':  
                            Job.objects.create(
                                name=job_name[0],
                                description=job_name[1]
                            )
                        # print('Job ', job_name[0], ' added')

                 #adding job end

                    ###
                #adding oil_place start
                for i in table_data['data']:
                    
                    reservoir_name = i[3]
                    try:
                        reservoir_inst = OilPlace.objects.get(name=reservoir_name)
                    except:
                        OilPlace.objects.create(
                            name=reservoir_name
                        )

                #adding oil_place end
                
                #adding employee start
                count=1
                for i in table_data['data']:
                    
                    employee_excel = i[1].split()
                    if len(employee_excel) == 2:
                        employee_excel.append(' .')
                    elif len(employee_excel) == 1:
                        employee_excel.append(' .')
                        employee_excel.append(' .')
                    try:
                        employee_inst = Employees.objects.get(
                            name = employee_excel[0],
                            surname = employee_excel[1],
                            middlename = employee_excel[2]
                        )
                    except:
                        empl_job = i[2].split(' ',1)
                        if empl_job:
                            try:
                                job_inst = Job.objects.get(
                                    name=empl_job[0]
                                )
                            except:
                                continue
                        empl_oilplace = i[3]
                        if empl_oilplace:
                            try:
                                oilplace_inst = OilPlace.objects.get(
                                    name=empl_oilplace
                                )
                            except:
                                continue
                        tarrif_category = len(i[4])

                        Employees.objects.create(
                            tabel_number = count,
                            name = employee_excel[0],
                            surname = employee_excel[1],
                            middlename = employee_excel[2],
                            tariff_category=tarrif_category,
                            job=job_inst,
                            oil_place=oilplace_inst
                        )
                        count+=1
                    #employee add end
                
                #graph adding start
                # graph_month = 1
                # graph_year = 2023
                
                table_data_month = table_data['month'].split()
                # print(table_data_month)
                print(len(table_data_month))
                graph_month = russian_month_to_int(table_data_month[0])
                graph_year =  int(table_data_month[1])
                
                graph_inst = None
                # print(graph_month)
                try:
                    graph_inst = Graph.objects.get(
                        month= graph_month,
                        year = graph_year
                    )
                except:
                    oilplace_inst = OilPlace.objects.get(name='Ботахан')
                    subdivision_inst = Subdivision.objects.get(name='БДН')
                    Graph.objects.create(
                        month = graph_month,
                        year = graph_year,
                        reservoir = oilplace_inst,
                        subdivision = subdivision_inst
                    )
                for row in table_data['data']:
                    employee_excel = row[1].split()
                    if len(employee_excel) == 2:
                        employee_excel.append(' .')
                    elif len(employee_excel) == 1:
                        employee_excel.append(' .')
                        employee_excel.append(' .')
                    try:
                        employee_inst = Employees.objects.get(
                            name = employee_excel[0],
                            surname = employee_excel[1],
                            middlename = employee_excel[2]
                        )
                    except:
                        continue
                    if graph_inst is not None and not graph_inst.employees.filter(tabel_number=employee_inst.tabel_number).exists():
                        graph_inst.employees.add(employee_inst)
                    graph_inst.save()

                    table_data_month = table_data['month'].split(' ')
                    #timetracking add start
                    for row in table_data['data']:
                        count_day = 1
                        length = len(row)
                        employee_excel = row[1].split()
                        if len(employee_excel) == 2:
                            employee_excel.append(' .')
                        elif len(employee_excel) == 1:
                            employee_excel.append(' .')
                            employee_excel.append(' .')
                            try:
                                employee_inst = Employees.objects.get(
                                    name = employee_excel[0],
                                    surname = employee_excel[1],
                                    middlename = employee_excel[2]
                                )
                            except:
                                continue
                        graph_year = 2023
                        if len(table_data_month) == 3:
                            graph_year = int(table_data_month[1])
                        else:
                            graph_year = int(table_data_month[2])
                        graph_month = russian_month_to_int(table_data_month[0])
                        
                        print('graph_month ',graph_month)
                        # Get the number of days in the current month
                        num_days_in_month = calendar.monthrange(graph_year, graph_month)[1]
                        
                        for value in row[5:length-4]:
                            # while count_day <= num_days_in_month:
                                try:
                                    timetracking_inst = TimeTracking.objects.get(
                                        employee_id = employee_inst,
                                        date=datetime.datetime(2023,graph_month,count_day)
                                    )
                                except:
                                    print('month ',month,' day ',count_day)
                                    if value is not None:
                                        TimeTracking.objects.create(
                                            employee_id = employee_inst,
                                            date=datetime.datetime(2023,graph_month,count_day),
                                            worked_hours = value
                                        )
                                count_day+=1
                            
                            # if  count_day > num_days_in_month:
                            #     count_day=1

                    graph_month = (graph_month % 12) + 1

                table_data['data'].clear()
        else:
            messages.error(request,'файл не xlsx формата :(')
    context = {}
    context.update(sidebar(request))
    return render(request,'graph/parsing_graph.html',context)








