from audioop import reverse
import calendar
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

    tabel_pk = request.session['chosen_pk']
    tabel = Tabel.objects.get(pk=tabel_pk)
    employees = tabel.employees.all()
    full_attendance = Attendance.objects.all()
    attendance = Attendance.objects.filter(type='дни явок')
    no_attendance = Attendance.objects.filter(type='дни неявок')
    tracking = TimeTracking.objects.all()
    
    month = tabel.month
    year = tabel.year

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

    #calculation attendance end

    

    

    context = {
        'tabel_pk':tabel_pk,
        "year":year,
        "month":month,
        'days':days,
        'full_attendance':full_attendance,
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

    tabel_pk = request.session['chosen_pk']
    tabel = Tabel.objects.get(pk=tabel_pk)
    employees = tabel.employees.all()
    attendance_full = Attendance.objects.all()
    attendance = Attendance.objects.filter(type='дни явок')
    no_attendance = Attendance.objects.filter(type='дни неявок')
    tracking = TimeTracking.objects.all()
    
    month = tabel.month
    year = tabel.year

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

    #calculation attendance end

    if request.method == "POST":
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

        return redirect(reverse('tabel:tabel_admin') +f'?tabel_pk={tabel_pk}')

    context = {
        'tabel_pk':tabel_pk,
        "year":year,
        "month":month,
        'days':days,
        'full_attendance':attendance_full,
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

    tabel_pk = request.session['chosen_pk']
    tabel = Tabel.objects.get(pk=tabel_pk)
    employees = tabel.employees.all()
    job = Job.objects.all()
    full_attendance = Attendance.objects.all()
    attendance = Attendance.objects.filter(type='дни явок')
    no_attendance = Attendance.objects.filter(type='дни неявок')
    tracking = TimeTracking.objects.all()
    month = tabel.month
    year = tabel.year

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
    dates = tracking.values_list('date',flat=True).distinct()
    for date in dates:
        month = date.month
        year = date.year
    
    num_days = calendar.monthrange(int(year),int(month))[1]
    days = range(1,num_days+1)

    if request.method == 'POST':
        for key,value in request.POST.items():
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
        'tabel_pk':tabel_pk,
        "year":year,
        "month":month,
        'days':days,
        'full_attendance':full_attendance,
        "selected_month": name_month_ru,
        'employees':employees,
        'attendance': attendance, 
        'no_attendance': no_attendance,
        'time_tracking': tracking,
        'tabel':tabel,
        'calculations': directory,
    }
    context.update(sidebar(request))

    return render(request,'tabel/tabel_admin_update.html',context)
