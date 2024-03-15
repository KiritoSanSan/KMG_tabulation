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
            verbose_name = 'Табель'
            verbose_name_plural = "Табеля"

    def __str__(self) -> str:
        return f"{self.id} {self.subdivision} {self.reservoir}"
    
class TabelEmployeesList(models.Model):
    employee = models.ForeignKey('graph.Employees', on_delete=models.CASCADE)
    tabel = models.ForeignKey(Tabel, on_delete=models.CASCADE,)

    class Meta:
        verbose_name = 'Работник'
        verbose_name_plural = "Работники"

