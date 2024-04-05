from django.db import models
from graph.models import OilPlace,Subdivision,Employees
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

class Tabel(models.Model):
    reservoir= models.ForeignKey('graph.OilPlace', verbose_name="Месторождение",related_name='tabel_reservoir', on_delete=models.CASCADE)
    subdivision = models.ForeignKey('graph.Subdivision', verbose_name="Подразделение", on_delete=models.CASCADE,related_name = 'tabel_subdivision')
    month = models.CharField(max_length = 100,verbose_name='Месяц',choices=MONTH_CHOICES_RU,default=None)
    year = models.CharField(verbose_name = 'Год',choices=YEARS_CHOICES,max_length=4,default=None)
    employees = models.ManyToManyField('graph.Employees',through="TabelEmployeesList",related_name='tabel_employee',verbose_name='Работники')

    class Meta:
            verbose_name = 'Согласованный Табель'
            verbose_name_plural = "Согласованные Табеля"

    def __str__(self) -> str:
        return f"{self.id} {self.subdivision} {self.reservoir}"
    
class TimeTrackingTabel(models.Model):
    employee_id = models.ForeignKey(Employees, verbose_name="Табельный Номер", on_delete=models.CASCADE)
    date = models.DateField(auto_now=False, auto_now_add=False, verbose_name = "Дата")
    worked_hours = models.CharField(max_length = 5, verbose_name = "Проработано часов",default="0",null=True)

    class Meta:
        verbose_name = 'Контроль времени работников Табеля'
        verbose_name_plural = "Контроль времени работников Табеля"
        # unique_together = ('date','employee_id')

    def __str__(self) -> str:
        return f"{self.id} {self.employee_id.name} {self.worked_hours}"

class TabelEmployeesList(models.Model):
    employee = models.ForeignKey(Employees, on_delete=models.CASCADE)
    tabel = models.ForeignKey(Tabel, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Работник'
        verbose_name_plural = "Работники"


class TabelApproved(models.Model):
    reservoir= models.ForeignKey('graph.OilPlace', verbose_name="Месторождение",related_name='tabel_approved_reservoir', on_delete=models.CASCADE)
    subdivision = models.ForeignKey('graph.Subdivision', verbose_name="Подразделение", on_delete=models.CASCADE,related_name = 'tabel_approved_subdivision')
    month = models.CharField(max_length = 100,verbose_name='Месяц',choices=MONTH_CHOICES_RU,default=None)
    year = models.CharField(verbose_name = 'Год',choices=YEARS_CHOICES,max_length=4,default=None)
    employees = models.ManyToManyField('graph.Employees',through="TabelApprovedEmployeesList",related_name='tabel_approved_employee',verbose_name='Работники')

    class Meta:
        verbose_name = 'Утвержденный Табель'
        verbose_name_plural = "Утвержденные Табеля"

    def __str__(self) -> str:
        return f"{self.id} {self.subdivision} {self.reservoir}"


class TabelApprovedEmployeesList(models.Model):
    employee = models.ForeignKey(Employees, on_delete=models.CASCADE)
    tabel = models.ForeignKey(TabelApproved, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Работник'
        verbose_name_plural = "Работники"
