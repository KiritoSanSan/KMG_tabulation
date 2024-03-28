import calendar
from django.shortcuts import render
from .models import *
from graph.models import Attendance, Graph, TimeTracking

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
        'graph':tabel,
        'calculations': directory,
    }
    return render(request,'tabel/tabel_admin.html',context)




