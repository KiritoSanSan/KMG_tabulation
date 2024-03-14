from .models import *
from django import forms

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