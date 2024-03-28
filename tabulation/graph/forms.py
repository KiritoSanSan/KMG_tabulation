from .models import *
from django import forms

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

class YearForm(forms.Form):
    year = forms.ChoiceField(choices=YEARS_CHOICES)

class GraphSubdivisionForm(forms.Form):
    subdivisions = Subdivision.objects.all()
    name_choices = [(subdivision.name, subdivision.name) for subdivision in subdivisions]
    name = forms.Select(choices=name_choices)


class GraphReservoirForm(forms.Form):
    oil_places = OilPlace.objects.all()
    name_choices = [(oil_place.name, oil_place.name) for oil_place in oil_places]
    name = forms.Select(choices=name_choices)

class YearSelectForm(forms.Form):
    years = [(year, str(year)) for year in range(2023, 2026)]  # Generate choices for 2023, 2024, 2025
    year = forms.ChoiceField(choices=years)


class GraphForm(forms.ModelForm):
    class Meta:
        model = Graph
        fields = ('__all__')

class EmployeeFormList(forms.Form):
    employees = Employees.objects.all()
    employee_choices = [(employee.tabel_number,employee.tabel_number) for employee in employees]
    choices = forms.Select(choices=employee_choices)

class TimeTrackingForm(forms.ModelForm):
    class Meta:
        model = TimeTracking
        fields = ('__all__')

class EmployeeCreateForm(forms.ModelForm):
    class Meta:
        model = Employees
        fields = ("__all__")
        


