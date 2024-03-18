from django.db import models
from django.forms import ValidationError
from django.urls import reverse
from django.contrib import messages
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
    ('дни неявок',"Дни Неявок"),
    ("дни явок","Дни Явок")
)
class Job(models.Model):
    name = models.CharField(max_length = 100, verbose_name = "Название",unique=True)
    description = models.CharField(max_length=200, verbose_name = "Описание")
    
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

    # month = models.IntegerField(choices=MONTH_CHOICES_RU, default = 0)
    # year = models.IntegerField(default = 2024)

    # @property
    # def days_in_month(self):
    #     if int(self.month) in [1, 3, 5, 7, 8, 10, 12]:
    #         return 31
    #     elif int(self.month) == 2:
    #         # Check if it's a leap year
    #         if self.year % 4 == 0 and (self.year % 100 != 0 or self.year % 400 == 0):
    #             return 29
    #         else:
    #             return 28
    #     else:
    #         return 30

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)

    #     for i in range(1, 32):
    #         if i > self.days_in_month:
    #             delattr(self, f'day_{i}')

    class Meta:
        verbose_name = 'Контроль времени работников'
        verbose_name_plural = "Контроль времени работников"
        unique_together = ('date','employee_id')

    def __str__(self) -> str:
        return f"{self.id} {self.employee_id.name} {self.worked_hours}"
    

    def create(self,validated_data):
         ...
    # @classmethod
    # def update_missing_fact_entries(cls, month, year):
    #     plan_entries = cls.objects.filter(type='plan', date__month=month, date__year=year)
    #     fact_entries = cls.objects.filter(type='fact', date__month=month, date__year=year)
    #     missing_entries = plan_entries.exclude(pk__in=fact_entries.values_list('pk', flat=True))

    #     for entry in missing_entries:
    #         if not cls.objects.filter(type='fact', employee_id=entry.employee_id, date=entry.date).exists():
    #             cls.objects.create(
    #                 employee_id=entry.employee_id,
    #                 date=entry.date,
    #                 worked_hours=entry.worked_hours,
    #                 type='fact'
    #             )

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
    description = models.CharField(max_length=200, verbose_name = "Описание")
    
    class Meta:
            verbose_name = 'Месторождение'
            verbose_name_plural = "Месторождения"
    
    def __str__(self) -> str:
        return self.name
    
class Subdivision(models.Model):
    name = models.CharField(max_length=50,verbose_name = "Название Подразделения",unique=True)
    description = models.CharField(max_length=200, verbose_name = "Описание")
    
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
        return f"{self.id} {self.subdivision} {self.reservoir}  "




class GraphEmployeesList(models.Model):
    employee_id = models.ForeignKey(Employees,related_name='employees_graph_employee',on_delete=models.CASCADE)
    graph_id = models.ForeignKey(Graph,related_name='employees_graph_graph',on_delete=models.CASCADE)
    
    class Meta:
            verbose_name = 'Работник'
            verbose_name_plural = "Работники"
            unique_together = ['employee_id','graph_id']
    
    def __str__(self):

        return f""
    
