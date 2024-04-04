from audioop import reverse
import calendar
import json

from django.shortcuts import get_object_or_404, redirect, render
from .models import *
from graph.models import Attendance, Graph , TimeTracking
from django.db.models import Q
from graph.views import sidebar
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from datetime import datetime
from django.shortcuts import redirect, render
from django.urls import reverse
from .models import *
from graph.views import sidebar
from graph.models import Attendance, Graph, Job, TimeTracking

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


    
def tabel_admin(request):
    if 'tabel_pk' in request.GET:
        tabel_pk = request.GET['tabel_pk']
        request.session['chosen_pk'] = tabel_pk
    #soglasovat' tabel
    if request.method == 'POST':
        # Check if the submitted form contains the key 'approve_graph'
        if 'approve_graph' in request.POST:
            tabel_pk = request.POST.get('tabel_pk')
            tabel_inst = Tabel.objects.get(pk=tabel_pk)
            # Create a Tabel instance with data from the chosen graph
            employees_graph = tabel_inst.employees.all()
            try:
                # Attempt to retrieve an existing Tabel instance
                tabel_instance = TabelApproved.objects.get(
                    reservoir=tabel_inst.reservoir,
                    subdivision=tabel_inst.subdivision,
                    month=tabel_inst.month,
                    year=tabel_inst.year,
                )
                if tabel_instance:
                    messages.error(request,'Табель уже согласован')
            except ObjectDoesNotExist:
                # If Tabel object doesn't exist, create it
                tabel_instance = TabelApproved.objects.create(
                    reservoir=tabel_inst.reservoir,
                    subdivision=tabel_inst.subdivision,
                    month=tabel_inst.month,
                    year=tabel_inst.year,
                )
                # tabel_instance.employees.add(employees_graph)
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
                return redirect(reverse('admin:tabel_tabelapproved_changelist'))
            

    tabel_pk = request.session['chosen_pk']
    tabel = Tabel.objects.get(pk=tabel_pk)
    employees = tabel.employees.all()
    attendance = Attendance.objects.filter(type='дни явок')
    no_attendance = Attendance.objects.filter(type='дни неявок')
    tracking = TimeTrackingTabel.objects.all()
    
    month = tabel.month
    year = tabel.year

    name_month_en = calendar.month_name[int(month)]
    name_month_ru = month_names_ru[name_month_en]

    if month and month is not None:
        filter_month = int(month)
        tracking = TimeTrackingTabel.objects.filter(employee_id__in = employees.values_list('tabel_number',flat=True))
        tracking = tracking.filter(date__month=filter_month)
        tabel_numbers = tracking.values_list('employee_id',flat=True)
        employees = employees.filter(tabel_number__in=tabel_numbers)
    if year and year is not None:
        filter_year = int(year)
        tracking = TimeTrackingTabel.objects.filter(employee_id__in = employees.values_list('tabel_number',flat=True))
        tracking = tracking.filter(date__year=filter_year)
        tabel_numbers = tracking.values_list('employee_id',flat=True)
        employees = employees.filter(tabel_number__in=tabel_numbers)
    dates = tracking.values_list('date',flat=True).distinct()
    for date in dates:
        month = date.month
        year = date.year
    
    num_days = calendar.monthrange(int(year),int(month))[1]
    days = range(1,num_days+1)

    #calculation attendace start
    # directory = {}
    # for employee in employees:
    #     pairs = [('worked_days', 0), ('weekends', 0), ('days_in_month', len(days)), ('total_work_hours', 0)]
    #     directory[f'{employee.name}'] = dict(pairs)

    # for employee in employees:
    #     for work in tracking:
    #         if work.employee_id == employee:
    #             if str(work.worked_hours).isdigit():
    #                 directory[f'{employee.name}']['worked_days'] += 1 
    #                 directory[f'{employee.name}']['total_work_hours'] += int(work.worked_hours)
    #             else:
    #                 directory[f'{employee.name}']['weekends'] += 1
    
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

    #calculation attendance end

    if request.method == "POST":
        print(request.POST)
        if request.headers["content-type"].strip().startswith("application/json"):
            if "employee_id_delete" in request.body.decode('utf-8'):
                employee_deletion_data = json.loads(request.body)
                employee_tabel_number = employee_deletion_data.get('employee_id_delete')
                empl = Employees.objects.get(pk=employee_tabel_number)
                tabel.employees.remove(empl)
                TimeTrackingTabel.objects.filter(employee_id = employee_tabel_number).delete()
                    
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
                            time_tracking_instance = TimeTrackingTabel.objects.get(pk=time_tracking_id)
                            time_tracking_instance.worked_hours = value
                            time_tracking_instance.save()
                        else:
                            TimeTrackingTabel.objects.create(
                                employee_id=time_tracking_employee,
                                date=datetime(int(year), int(month), day),
                                worked_hours="0",
                            )
                else:
                    time_tracking_id = key.split('_')[2]
                    time_tracking_instance = TimeTrackingTabel.objects.get(pk=time_tracking_id)
                    time_tracking_instance.worked_hours = value
                    time_tracking_instance.save()

        return redirect(reverse('tabel:tabel_admin') +f'?tabel_pk={tabel_pk}')

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
    }
    context.update(sidebar(request))
    return render(request,'tabel/tabel_admin.html',context)



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
    tracking = TimeTrackingTabel.objects.all()
    
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


    month = tabel.month
    year = tabel.year

    name_month_en = calendar.month_name[int(month)]
    name_month_ru = month_names_ru[name_month_en]

    if month and month is not None:
        filter_month = int(month)
        tracking = TimeTrackingTabel.objects.filter(employee_id__in = employees.values_list('tabel_number',flat=True))
        tracking = tracking.filter(date__month=filter_month)
        tabel_numbers = tracking.values_list('employee_id',flat=True)
        employees = employees.filter(tabel_number__in=tabel_numbers)
    if year and year is not None:
        filter_year = int(year)
        tracking = TimeTrackingTabel.objects.filter(employee_id__in = employees.values_list('tabel_number',flat=True))
        tracking = tracking.filter(date__year=filter_year)
        tabel_numbers = tracking.values_list('employee_id',flat=True)
        employees = employees.filter(tabel_number__in=tabel_numbers)
    dates = tracking.values_list('date',flat=True).distinct()
    for date in dates:
        month = date.month
        year = date.year
    
    num_days = calendar.monthrange(int(year),int(month))[1]
    days = range(1,num_days+1)

    #calculation attendace start
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

    #calculation attendance end

    if request.method == "POST":
        print(request.POST)
        if request.headers["content-type"].strip().startswith("application/json"):
            if "employee_id_delete" in request.body.decode('utf-8'):
                employee_deletion_data = json.loads(request.body)
                employee_tabel_number = employee_deletion_data.get('employee_id_delete')
                empl = Employees.objects.get(pk=employee_tabel_number)
                tabel.employees.remove(empl)
                TimeTrackingTabel.objects.filter(employee_id = employee_tabel_number).delete()
                    
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
                            time_tracking_instance = TimeTrackingTabel.objects.get(pk=time_tracking_id)
                            time_tracking_instance.worked_hours = value
                            time_tracking_instance.save()
                        else:
                            TimeTrackingTabel.objects.create(
                                employee_id=time_tracking_employee,
                                date=datetime(int(year), int(month), day),
                                worked_hours="0",
                            )
                else:
                    time_tracking_id = key.split('_')[2]
                    time_tracking_instance = TimeTrackingTabel.objects.get(pk=time_tracking_id)
                    time_tracking_instance.worked_hours = value
                    time_tracking_instance.save()

        return redirect(reverse('tabel:tabel_admin') +f'?tabel_pk={tabel_pk}')
                        


    #calculation attendace start
    directory = {}
    for employee in employees:
        pairs = []
        pairs.append(('worked_days', 0))
        for att in full_attendance:
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
    }
    context.update(sidebar(request))

    return render(request,'tabel/tabel_admin_update.html',context)

def tabel_approved_admin(request):
    if 'tabel_pk' in request.GET:
        tabel_pk = request.GET['tabel_pk']
        request.session['chosen_pk'] = tabel_pk
    tabel_pk = request.session['chosen_pk']
    tabel = TabelApproved.objects.get(pk=tabel_pk)
    employees = tabel.employees.all()
    attendance = Attendance.objects.filter(type='дни явок')
    no_attendance = Attendance.objects.filter(type='дни неявок')
    tracking = TimeTrackingTabel.objects.all()
    
    month = tabel.month
    year = tabel.year

    name_month_en = calendar.month_name[int(month)]
    name_month_ru = month_names_ru[name_month_en]

    if month and month is not None:
        filter_month = int(month)
        tracking = TimeTrackingTabel.objects.filter(employee_id__in = employees.values_list('tabel_number',flat=True))
        tracking = tracking.filter(date__month=filter_month)
        tabel_numbers = tracking.values_list('employee_id',flat=True)
        employees = employees.filter(tabel_number__in=tabel_numbers)
    if year and year is not None:
        filter_year = int(year)
        tracking = TimeTrackingTabel.objects.filter(employee_id__in = employees.values_list('tabel_number',flat=True))
        tracking = tracking.filter(date__year=filter_year)
        tabel_numbers = tracking.values_list('employee_id',flat=True)
        employees = employees.filter(tabel_number__in=tabel_numbers)
    dates = tracking.values_list('date',flat=True).distinct()
    for date in dates:
        month = date.month
        year = date.year
    
    num_days = calendar.monthrange(int(year),int(month))[1]
    days = range(1,num_days+1)
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

    #calculation attendance end

    if request.method == "POST":
        print(request.POST)
        if request.headers["content-type"].strip().startswith("application/json"):
            if "employee_id_delete" in request.body.decode('utf-8'):
                employee_deletion_data = json.loads(request.body)
                employee_tabel_number = employee_deletion_data.get('employee_id_delete')
                empl = Employees.objects.get(pk=employee_tabel_number)
                tabel.employees.remove(empl)
                TimeTrackingTabel.objects.filter(employee_id = employee_tabel_number).delete()
                    
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
                            time_tracking_instance = TimeTrackingTabel.objects.get(pk=time_tracking_id)
                            time_tracking_instance.worked_hours = value
                            time_tracking_instance.save()
                        else:
                            TimeTrackingTabel.objects.create(
                                employee_id=time_tracking_employee,
                                date=datetime(int(year), int(month), day),
                                worked_hours="0",
                            )
                else:
                    time_tracking_id = key.split('_')[2]
                    time_tracking_instance = TimeTrackingTabel.objects.get(pk=time_tracking_id)
                    time_tracking_instance.worked_hours = value
                    time_tracking_instance.save()

        return redirect(reverse('tabel:tabel_admin') +f'?tabel_pk={tabel_pk}')

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
    }
    context.update(sidebar(request))
    return render(request,'tabel/tabel_approved_admin.html',context)



