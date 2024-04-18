from django.db import models
from django.forms import ValidationError
from django.urls import reverse
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.db.models import Q

from django.contrib import messages
import datetime

# from tabulation import graph
# Create your models here.
MONTH_CHOICES_RU = (
    ("1", "Январь"),
    ("2", "Февраль"),
    ("3", "Март"),
    ("4", "Апрель"),
    ("5", "Май"),
    ("6", "Июнь"),
    ("7", "Июль"),
    ("8", "Август"),
    ("9", "Сентябрь"),
    ("10", "Октябрь"),
    ("11", "Ноябрь"),
    ("12", "Декабрь"),
)
YEARS_CHOICES = (
    ('2023','2023'),
    ('2024','2024'),
    ('2025','2025')
)
ATTENDACE_CHOICES = (
    ("дни явок","Дни Явок"),
    ('дни неявок',"Дни Неявок")
)
class Job(models.Model):
    name = models.CharField(max_length = 100, verbose_name = "Название",unique=True)
    description = models.CharField(max_length=200, verbose_name = "Описание",null=True)
    
    class Meta:
            verbose_name = 'Должность'
            verbose_name_plural = "Должности"

    def __str__(self) -> str:
        return self.name

    
class Employees(models.Model):
    tabel_number = models.BigIntegerField(primary_key = True, verbose_name = "Табельный Номер Работника")
    name = models.CharField(max_length=50, verbose_name = "Имя")
    middlename = models.CharField(max_length=50, verbose_name = "Отчество")
    surname = models.CharField(max_length=50, verbose_name = "Фамилия")
    tariff_category = models.IntegerField(verbose_name = "Тарифная категория")
    job = models.ForeignKey(Job, verbose_name='Работа',related_name='job', on_delete=models.CASCADE)
    oil_place = models.ForeignKey('OilPlace',verbose_name='Месторождение', related_name='reservoir', on_delete=models.CASCADE)
    
    @property
    def fullname(self):
        return f"{self.surname} {self.name} {self.middlename}"
    
    class Meta:
        verbose_name = 'Работник'
        verbose_name_plural = 'Работники'
        # unique_together = ('')

    def __str__(self) -> str:
        return f"{self.tabel_number} {self.name} {self.surname}"

class TimeTracking(models.Model):
    employee_id = models.ForeignKey(Employees, verbose_name="Табельный Номер", on_delete=models.CASCADE)
    date = models.DateField(auto_now=False, auto_now_add=False, verbose_name = "Дата")
    worked_hours = models.CharField(max_length = 5, verbose_name = "Проработано часов",default="0",null=True)

    class Meta:
        verbose_name = 'Контроль времени работников Графика'
        verbose_name_plural = "Контроль времени работников Графика"
        # unique_together = ('date','employee_id')

    def __str__(self) -> str:
        return f"{self.id} {self.employee_id.name} {self.worked_hours}"
        


class Attendance(models.Model):
    name = models.CharField(max_length=50, verbose_name = "Название")
    description = models.CharField(max_length=200, verbose_name = "Описание")
    type = models.CharField(verbose_name="Тип", max_length=100,choices=ATTENDACE_CHOICES)
    
    class Meta:
        verbose_name = 'Явка'
        verbose_name_plural = "Явки"

    def __str__(self) -> str:
        return self.name
    

class OilPlace(models.Model):
    name = models.CharField(max_length=50, verbose_name = "Название Месторождения",unique=True)
    # description = models.CharField(max_length=200, verbose_name = "Описание")
    
    class Meta:
        verbose_name = 'Месторождение'
        verbose_name_plural = "Месторождения"
    
    def __str__(self) -> str:
        return self.name
    
class Subdivision(models.Model):
    name = models.CharField(max_length=50,verbose_name = "Название Подразделения",unique=True)
    # description = models.CharField(max_length=200, verbose_name = "Описание")
    
    class Meta:
        verbose_name = 'Подразделение'
        verbose_name_plural = "Подразделения"

    def __str__(self) -> str:
        return self.name

class Graph(models.Model):
    reservoir= models.ForeignKey(OilPlace, verbose_name="Месторождение",related_name='graph_reservoir', on_delete=models.CASCADE)
    subdivision = models.ForeignKey(Subdivision, verbose_name="Подразделение", on_delete=models.CASCADE,related_name = 'graph_subdivision')
    month = models.CharField(max_length = 100,verbose_name='Месяц',choices=MONTH_CHOICES_RU,default=None)
    year = models.CharField(verbose_name = 'Год',choices=YEARS_CHOICES,max_length=4,default=None)
    employees = models.ManyToManyField(Employees,through="GraphEmployeesList",related_name='graph_employee',verbose_name='Работники')

    class Meta:
        verbose_name = 'График'
        verbose_name_plural = "Графики"
        unique_together = ('reservoir', 'subdivision','month','year')


    def __str__(self) -> str:
        return f"{self.id} {self.subdivision} {self.reservoir}"
    
    # @receiver(pre_delete, sender=TimeTracking)
    # def delete(self,sender,instance, *args, **kwargs):
    #     # Get all employees related to this graph
    #     # graph = Graph.objects.get(pk=graph_pk)
    #     graph_employees = instance.employees.all()
    #     month = instance.month
    #     year = instance.year

    #     # Delete corresponding time tracking entries for each employee
    #     for employee in graph_employees:
    #         TimeTracking.objects.filter(employee_id=employee, date__month=month, date__year=year).delete()
    #     print('delete gtaph')
    #     # Now delete the graph itself
    #     return super(Graph, self).delete(*args, **kwargs)

# class TimeTrackingGraph(models.Model):
#     timetracking = models.ForeignKey(TimeTracking,on_delete=models.CASCADE)
#     employee = models.ForeignKey(Employees,on_delete=models.CASCADE)
#     graph = models.ForeignKey(Graph,on_delete=models.CASCADE)
#     date = models.DateField(auto_now=False, auto_now_add=False, verbose_name = "Дата")
#     worked_hours = models.CharField(max_length = 5, verbose_name = "Проработано часов",default="0",null=True)


class GraphEmployeesList(models.Model):
    employee_id = models.ForeignKey(Employees,related_name='employees_graph_employee',on_delete=models.CASCADE)
    graph_id = models.ForeignKey(Graph,related_name='employees_graph_graph',on_delete=models.CASCADE)
    
    class Meta:
            verbose_name = 'Работник'
            verbose_name_plural = "Работники"
            unique_together = ['employee_id','graph_id']
    
    def __str__(self):

        return f""
    
