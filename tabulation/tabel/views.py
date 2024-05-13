# from audioop import reverse
import calendar
import json

from django.shortcuts import get_object_or_404, redirect, render
from .models import *
from graph.decorators import allowed_users
from graph.models import Attendance
from django.db.models import Q
from graph.views import sidebar

from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.urls import reverse

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

@login_required(login_url='admin/login/')
@allowed_users(allowed_roles=['Табельщик', 'Администратор', 'Руководитель'])
def tabel_admin(request):
    if 'tabel_pk' in request.GET:
        tabel_pk = request.GET['tabel_pk']
        request.session['chosen_pk'] = tabel_pk

    

    tabel_pk = request.session['chosen_pk']
    tabel = Tabel.objects.get(pk=tabel_pk)
    employees = tabel.employees.all()
    attendance = Attendance.objects.filter(type='дни явок')
    no_attendance = Attendance.objects.filter(type='дни неявок')
    month = tabel.month
    year = tabel.year
    tracking = TimeTrackingTabel.objects.filter(date__year=int(year), date__month=int(month)).select_related('employee_id')
    
    

    name_month_en = calendar.month_name[int(month)]
    name_month_ru = month_names_ru[name_month_en]
    num_days = calendar.monthrange(int(year),int(month))[1]
    days = range(1,num_days+1)

    #calculation attendace
    directory = {}
    for employee in employees:
        pairs = []
        pairs.append(('worked_days', 0))
        for att in attendance:
            pairs.append((f'{att}', 0))
        for att in no_attendance:
            pairs.append((f'{att}', 0))
        pairs.append(('days_in_month', len(days)))
        pairs.append(('total_work_hours', 0))
        pairs.append(('night_work',0))
        directory[int(f'{employee.tabel_number}')] = dict(pairs)

    # for employee in employees:
    for work in tracking:
        # if work.employee_id == employee:
            if str(work.worked_hours).isdigit():
                directory[int(f'{work.employee_id.tabel_number}')]['worked_days'] += 1
                directory[int(f'{work.employee_id.tabel_number}')]['total_work_hours'] += int(work.worked_hours)
            
            #night worked hours
            sep = work.worked_hours.split('/')
            if len(sep)==2:
                if str(sep[1]).isdigit():
                    directory[int(f'{work.employee_id.tabel_number}')]['night_work'] +=int(sep[1])
                    directory[int(f'{work.employee_id.tabel_number}')]['total_work_hours'] += int(sep[0])
            #

            for dir in directory[int(f'{work.employee_id.tabel_number}')].keys():
                if dir == work.worked_hours:
                    directory[int(f'{work.employee_id.tabel_number}')][f'{dir}'] += 1
    print(directory)
    time_tracking_dict = {}
    for employee in employees:
        list = []
        for day in days:
            list.append(0)
        time_tracking_dict[int(f'{employee.tabel_number}')] = list

    for work in tracking:
        employee_id = work.employee_id.tabel_number
        day_index = days.index(work.date.day)
        time_tracking_dict[int(employee_id)][day_index] = work.worked_hours
    
    if request.method == 'POST':
        if 'approve_graph' in request.POST:
            tabel_pk = request.POST.get('tabel_pk')
            tabel_inst = Tabel.objects.get(pk=tabel_pk)
            employees_graph = tabel_inst.employees.all()
            try:
                tabel_instance = TabelApproved.objects.get(
                    reservoir=tabel_inst.reservoir,
                    subdivision=tabel_inst.subdivision,
                    month=tabel_inst.month,
                    year=tabel_inst.year,
                )
                if tabel_instance:
                    messages.error(request,'Табель уже утвержден')
            except ObjectDoesNotExist:
                tabel_instance = TabelApproved.objects.create(
                    reservoir=tabel_inst.reservoir,
                    subdivision=tabel_inst.subdivision,
                    month=tabel_inst.month,
                    year=tabel_inst.year,
                )
                time_tracking_dict_tabel = {}
                for employee in employees_graph:
                    list = []
                    for day in days:
                        list.append(0)
                    time_tracking_dict_tabel[int(f'{employee.tabel_number}')] = list
                for work in tracking:
                    employee_id = work.employee_id.tabel_number
                    day_index = days.index(work.date.day)
                    time_tracking_dict_tabel[int(employee_id)][day_index] = work.worked_hours
                time_tracking_tabel_instances = []
                for employee_id, values in time_tracking_dict_tabel.items():
                    for day_index, worked_hours in enumerate(values):
                        time_tracking_tabel_instances.append(TimeTrackingTabel(
                            employee_id=Employees.objects.get(tabel_number=employee_id),
                            date=datetime(int(tabel_instance.year), int(tabel_instance.month), days[day_index]),
                            worked_hours=worked_hours
                        ))
                # print(time_tracking_tabel_instances)
                TabelApprovedTimeTracking.objects.bulk_create(time_tracking_tabel_instances)
                tabel_instance.employees.set(employees_graph)
                # for employee in employees_graph:
                #     time_tracking = TimeTrackingTabel.objects.filter(employee_id=employee).select_related('employee_id').values()
                #     employee_instance = Employees.objects.get(pk=employee.tabel_number)
                #     for value in time_tracking:
                #         TabelApprovedTimeTracking.objects.create(
                #             employee_id = employee_instance,
                #             date = value['date'],
                #             worked_hours = value['worked_hours']
                #         )
            
                tabel_instance.employees.set(employees_graph)
                messages.success(request,'Табель утвержден')
                return redirect(reverse('admin:tabel_tabelapproved_changelist'))
            

    context = {
        'tabel_pk':tabel_pk,
        "year":year,
        "month":month,
        'days':days,
        "selected_month": name_month_ru,
        'employees':employees,
        'attendance': attendance, 
        'no_attendance': no_attendance,
        'time_tracking': tracking,
        'tabel':tabel,
        'calculations': directory,
        'time_tracking_dict': time_tracking_dict,

    }
    context.update(sidebar(request))
    return render(request,'tabel/tabel_admin.html',context)


@login_required(login_url='admin/login/')
@allowed_users(allowed_roles=['Табельщик', 'Администратор'])
def tabel_admin_update(request):
    if 'tabel_pk' in request.GET:
        tabel_pk = request.GET['tabel_pk']
        request.session['chosen_pk'] = tabel_pk

    search_text = request.POST.get('time_tracking_set-prefix-employee_id')
    tabel_pk = request.session['chosen_pk']
    tabel = Tabel.objects.get(pk=tabel_pk)
    employees = tabel.employees.all()
    full_attendance = Attendance.objects.all()
    attendance = Attendance.objects.filter(type='дни явок')
    no_attendance = Attendance.objects.filter(type='дни неявок')
    month = tabel.month
    year = tabel.year
    tracking = TimeTrackingTabel.objects.filter(date__year=int(year), date__month=int(month)).select_related('employee_id')
    
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


    

    name_month_en = calendar.month_name[int(month)]
    name_month_ru = month_names_ru[name_month_en]

    # if month and month is not None:
    #     filter_month = int(month)
    #     tracking = TimeTrackingTabel.objects.filter(employee_id__in = employees.values_list('tabel_number',flat=True))
    #     tracking = tracking.filter(date__month=filter_month)
    #     tabel_numbers = tracking.values_list('employee_id',flat=True)
    #     employees = employees.filter(tabel_number__in=tabel_numbers)
    # if year and year is not None:
    #     filter_year = int(year)
    #     tracking = TimeTrackingTabel.objects.filter(employee_id__in = employees.values_list('tabel_number',flat=True))
    #     tracking = tracking.filter(date__year=filter_year)
    #     tabel_numbers = tracking.values_list('employee_id',flat=True)
    #     employees = employees.filter(tabel_number__in=tabel_numbers)
    # dates = tracking.values_list('date',flat=True).distinct()
    # for date in dates:
    #     month = date.month
    #     year = date.year
    
    num_days = calendar.monthrange(int(year),int(month))[1]
    days = range(1,num_days+1)

    time_tracking_dict = {}
    for employee in employees:
        list = []
        for day in days:
            list.append(0)
        time_tracking_dict[int(f'{employee.tabel_number}')] = list
    # print(time_tracking_dict)

    for work in tracking:
        employee_id = work.employee_id.tabel_number
        day_index = days.index(work.date.day)
        time_tracking_dict[int(employee_id)][day_index] = work.worked_hours

    if request.method == "POST":
        # AJAX requests 
        if request.headers["content-type"].strip().startswith("application/json"):
            if "employee_id_delete" in request.body.decode('utf-8'):
                employee_deletion_data = json.loads(request.body)
                employee_tabel_number = employee_deletion_data.get('employee_id_delete')
                empl = Employees.objects.get(pk=employee_tabel_number)
                tabel.employees.remove(empl)
                tracking.filter(employee_id = employee_tabel_number).delete()

                # TimeTrackingTabel.objects.filter(employee_id = employee_tabel_number).delete()
                    
            if "employee_id" in request.body.decode('utf-8'):
                employee_addition_data = json.loads(request.body)
                employee_tabel_number = employee_addition_data.get('employee_id')
                empl = Employees.objects.get(pk=employee_tabel_number)
                for day in days:
                    TimeTrackingTabel.objects.create(
                        employee_id = empl,
                        date = datetime(year, month, day),
                        worked_hours = ''
                    )
                tabel.employees.add(employee_tabel_number)

        for key,value in request.POST.items():
            if key.startswith('worked_hours_'):
                time_tracking_day = int(key.split('_')[4])
                key_parts = key.split('_')
                if len(key_parts) >=5:
                    for day in days:
                        time_tracking_employee = int(key.split('_')[2])
                        if day == time_tracking_day:
                                day_index = days.index(time_tracking_day)
                                time_tracking_dict[time_tracking_employee][day_index] = value
                        else:
                            if time_tracking_employee not in time_tracking_dict:
                                time_tracking_dict[time_tracking_employee] = [0] * len(days)
                            
                            # if time_tracking_day in days:
                            #     day_index = days.index(time_tracking_day)
                            #     time_tracking_dict[time_tracking_employee][day_index] = value
                else:
                    day_index = days.index(time_tracking_day)
                    time_tracking_dict[time_tracking_employee][day_index] = value
        for work in tracking:
            employee_id = work.employee_id.tabel_number
            if employee_id in time_tracking_dict:
                # print(f'{employee_id} is in time_tracking_dict')
                day = work.date.day
                if day in days:
                    day_index = days.index(day)
                    w = time_tracking_dict[employee_id][day_index]
                    if w is not None:
                        if w == '':
                            work.worked_hours = 0
                        else:
                            work.worked_hours = w
        # Batch save all the updated works
        TimeTrackingTabel.objects.bulk_update(tracking, ['worked_hours'])

        return redirect(reverse('tabel:tabel_admin') +f'?tabel_pk={tabel_pk}')
                        
    #calculation attendace  
    directory = {}
    for employee in employees:
        pairs = []
        pairs.append(('worked_days', 0))
        for att in attendance:
            pairs.append((f'{att}', 0))
        for att in no_attendance:
            pairs.append((f'{att}', 0))
        pairs.append(('days_in_month', len(days)))
        pairs.append(('total_work_hours', 0))
        pairs.append(('night_work',0))
        directory[int(f'{employee.tabel_number}')] = dict(pairs)

    # for employee in employees:
    for work in tracking:
        # if work.employee_id == employee:
        if str(work.worked_hours).isdigit():
            directory[int(f'{work.employee_id.tabel_number}')]['worked_days'] += 1
            directory[int(f'{work.employee_id.tabel_number}')]['total_work_hours'] += int(work.worked_hours)
            
            #night worked hours
            sep = work.worked_hours.split('/')
            if len(sep)==2:
                if str(sep[1]).isdigit():
                    directory[int(f'{work.employee_id.tabel_number}')]['night_work'] +=int(sep[1])
                    directory[int(f'{work.employee_id.tabel_number}')]['total_work_hours'] += int(sep[0])
            #
        
        for dir in directory[int(f'{work.employee_id.tabel_number}')].keys():
            if dir == work.worked_hours:
                directory[int(f'{work.employee_id.tabel_number}')][f'{dir}'] += 1
    print(directory)
    context = {
        'graph_pk':tabel_pk,
        "year":year,
        "month":month,
        'days':days,
        'full_attendance':full_attendance,
        "selected_month": name_month_ru,
        'employees':employees,
        'employees_all': search_employee,
        'attendance_all': full_attendance, 
        'attendance': attendance, 
        'no_attendance': no_attendance,
        'time_tracking': tracking,
        'tabel':tabel,
        'calculations': directory,
        'time_tracking_dict': time_tracking_dict,

    }
    context.update(sidebar(request))

    return render(request,'tabel/tabel_admin_update.html',context)

@login_required(login_url='admin/login/')
@allowed_users(allowed_roles=['Табельщик', 'Администратор', 'Руководитель'])
def tabel_approved_admin(request):
    if 'tabel_pk' in request.GET:
        tabel_pk = request.GET['tabel_pk']
        request.session['chosen_pk'] = tabel_pk
    tabel_pk = request.session['chosen_pk']
    tabel = TabelApproved.objects.get(pk=tabel_pk)
    employees = tabel.employees.all()
    attendance = Attendance.objects.filter(type='дни явок')
    no_attendance = Attendance.objects.filter(type='дни неявок')
    # tracking = TabelApprovedTimeTracking.objects.all()
    month = tabel.month
    year = tabel.year
    tracking = TabelApprovedTimeTracking.objects.filter(date__year=int(year), date__month=int(month)).select_related('employee_id')

    

    name_month_en = calendar.month_name[int(month)]
    name_month_ru = month_names_ru[name_month_en]

    # if month and month is not None:
    #     filter_month = int(month)
    #     tracking = TabelApprovedTimeTracking.objects.filter(employee_id__in = employees.values_list('tabel_number',flat=True))
    #     tracking = tracking.filter(date__month=filter_month)
    #     tabel_numbers = tracking.values_list('employee_id',flat=True)
    #     employees = employees.filter(tabel_number__in=tabel_numbers)
    # if year and year is not None:
    #     filter_year = int(year)
    #     tracking = TabelApprovedTimeTracking.objects.filter(employee_id__in = employees.values_list('tabel_number',flat=True))
    #     tracking = tracking.filter(date__year=filter_year)
    #     tabel_numbers = tracking.values_list('employee_id',flat=True)
    #     employees = employees.filter(tabel_number__in=tabel_numbers)
    # dates = tracking.values_list('date',flat=True).distinct()
    # for date in dates:
    #     month = date.month
    #     year = date.year
    
    num_days = calendar.monthrange(int(year),int(month))[1]
    days = range(1,num_days+1)

    #calculation attendance 
    directory = {}
    for employee in employees:
        pairs = []
        pairs.append(('worked_days', 0))
        #
        #
        for att in attendance:
            pairs.append((f'{att}', 0))
        for att in no_attendance:
            pairs.append((f'{att}', 0))
        pairs.append(('days_in_month', len(days)))
        pairs.append(('total_work_hours', 0))
        pairs.append(('night_work',0))
        directory[int(f'{employee.tabel_number}')] = dict(pairs)

    # for employee in employees:
    for work in tracking:
            # if work.employee_id == employee:
        if str(work.worked_hours).isdigit():
            directory[int(f'{work.employee_id.tabel_number}')]['worked_days'] += 1
            directory[int(f'{work.employee_id.tabel_number}')]['total_work_hours'] += int(work.worked_hours)
        #night worked hours
        sep = work.worked_hours.split('/')
        if len(sep)==2:
            if str(sep[1]).isdigit():
                directory[int(f'{work.employee_id.tabel_number}')]['night_work'] +=int(sep[1])
                directory[int(f'{work.employee_id.tabel_number}')]['total_work_hours'] += int(sep[0])
            #
        for dir in directory[int(f'{work.employee_id.tabel_number}')].keys():
            if dir == work.worked_hours:
                directory[int(f'{work.employee_id.tabel_number}')][f'{dir}'] += 1
    time_tracking_dict = {}
    for employee in employees:
        list = []
        for day in days:
            list.append(0)
        time_tracking_dict[int(f'{employee.tabel_number}')] = list

    for work in tracking:
        employee_id = work.employee_id.tabel_number
        day_index = days.index(work.date.day)
        time_tracking_dict[int(employee_id)][day_index] = work.worked_hours


    context = {
        'tabel_pk':tabel_pk,
        "year":year,
        "month":month,
        'days':days,
        "selected_month": name_month_ru,
        'employees':employees,
        'attendance': attendance, 
        'no_attendance': no_attendance,
        'time_tracking': tracking,
        'tabel':tabel,
        'calculations': directory,
        'time_tracking_dict': time_tracking_dict,

    }
    context.update(sidebar(request))
    return render(request,'tabel/tabel_approved_admin.html',context)