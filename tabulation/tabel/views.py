import calendar
import json

from django.shortcuts import get_object_or_404, redirect, render
from .models import *
from graph.models import Attendance, Graph , TimeTracking
from django.db.models import Q
from graph.views import sidebar
from django.http import JsonResponse
from django.db.models import Sum

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


    
def tabel_admin(request):
    if 'tabel_pk' in request.GET:
        tabel_pk = request.GET['tabel_pk']
        request.session['chosen_pk'] = tabel_pk

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

    context = {
        'graph_pk':tabel_pk,
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
    attendance_all = Attendance.objects.all()
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
        # AJAX requests 
        
        if request.headers["content-type"].strip().startswith("application/json"):
            # print(request.body.decode('utf-8'))
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

            # elif "tracking_id" in request.body.decode('utf-8'):
            #     data = json.loads(request.body)
            #     tracking_id = data["tracking_id"]
            #     # tracking_orig = TimeTrackingTabel.objects.get(pk=tracking_id).worked_hours
            #     day = data["day"]
            #     employee_tabel_number = data["employee_tabel_number"]
            #     # employee_tabel = tabel.employees.get(pk = data["employee_tabel_number"])
            #     worked_hours = data["worked_hours"]

            #     TimeTrackingTabel.objects.filter(pk=tracking_id).update(worked_hours=worked_hours)
                
            #     total_worked_hours = TimeTrackingTabel.objects.filter(employee_id=employee_tabel_number).aggregate(total=Sum('worked_hours'))['total'] or 0
                
            #     days_worked = TimeTrackingTabel.objects.filter(employee_id=employee_tabel_number, worked_hours__isnull=False).count()
                
            #     variables_count = len(directory[int(f'{employee_tabel_number}')])
                
            #     calculated_data = {
            #         "total_worked_hours": total_worked_hours,
            #         "days_worked": days_worked,
            #         "variables_count": variables_count,
            #     }

            #     return JsonResponse(calculated_data)

                # for employee in employees:
                #     if employee.tabel_number == employee_tabel_number:
                #         if worked_hours == '' and tracking_orig != '': # Deleted
                #             if not str(tracking_orig).isdigit():
                #                 for dir in directory[f'{employee.name}'].keys():
                #                     if dir == tracking_orig:
                #                         directory[f'{employee.name}'][f'{dir}'] -= 1
                #             else:
                #                 directory[f'{employee.name}']['worked_days'] -= 1
                #                 directory[f'{employee.name}']['total_work_hours'] -= tracking_orig

                #         elif worked_hours != '' and tracking_orig == '': # Added
                #             if not str(tracking_orig).isdigit():
                #                 for dir in directory[f'{employee.name}'].keys():
                #                     if dir == tracking_orig:
                #                         directory[f'{employee.name}'][f'{dir}'] += 1
                #             # else:

                                

                #         directory[f'{employee.name}']['worked_days'] += 1
                #         directory[f'{employee.name}']['total_work_hours'] += int(worked_hours) - tracking_orig

                # return JsonResponse({'success': True, 'directory': directory})

        for key, value in request.POST.items():
            # print(request.POST)
            if key.startswith('worked_hours_'):
                time_tracking_day = int(key.split('_')[4])  
                key_parts = key.split('_')
                print(key_parts)
                if len(key_parts) > 5:
                    for day in days:
                        time_tracking_employee = key.split('_')[4] + "_" + key.split('_')[5]
                        if day == time_tracking_day:
                            time_tracking_id = key.split('_')[3]
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
                    time_tracking_id = key.split('_')[3]
                    time_tracking_instance = TimeTrackingTabel.objects.get(pk=time_tracking_id)
                    time_tracking_instance.worked_hours = value
                    time_tracking_instance.save()

        return redirect(reverse('tabel:tabel_admin') +f'?tabel_pk={tabel_pk}')

    context = {
        'graph_pk':tabel_pk,
        "year":year,
        "month":month,
        'days':days,
        "selected_month": name_month_ru,
        'employees':employees,
        'employees_all': search_employee,
        'attendance_all': attendance_all, 
        'attendance': attendance, 
        'no_attendance': no_attendance,
        'time_tracking': tracking,
        'tabel':tabel,
        'calculations': directory,
    }
    context.update(sidebar(request))
    return render(request,'tabel/tabel_admin_update.html',context)



