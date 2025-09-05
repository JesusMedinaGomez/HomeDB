from django import forms
from django.forms import ModelForm
from .models import Objects, PlaceLabel, ObjType

class CreateObjForm(forms.ModelForm):
    class Meta:
        model = Objects
        exclude = ['user','datereg']
        labels = {
            'name': 'Nombre del objeto',
            'description': 'Descripción',
            'label': 'Tipo de objeto',
            'placelabel': 'Lugar',
            'important': '¿Es importante?',
            'whoIsIt': 'Propietario',
            'hasIt': '¿Se lo prestaste a...?',
            'isInPlace': '¿Está en su lugar?',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'label': forms.Select(attrs={'class': 'form-select'}),
            'placelabel': forms.Select(attrs={'class': 'form-select'}),
            'important': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'whoIsIt': forms.TextInput(attrs={'class': 'form-control'}),
            'isInPlace': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # si no se pasa, None
        super().__init__(*args, **kwargs)
        if user:
            self.fields['label'].queryset = ObjType.objects.filter(user=user)
            self.fields['placelabel'].queryset = PlaceLabel.objects.filter(user=user)



class CreatePlaceForm(forms.ModelForm):
    class Meta:
        model = PlaceLabel
        exclude = ['user','pseudonym']
        labels = {
            'name': 'Nombre del lugar',
            'description': 'Descripción',
            'isFull': '¿Está lleno?',
            'isEmpty': '¿Está vacío?',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'isFull': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'isEmpty': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class CreateObjTypeForm(forms.ModelForm):
    class Meta:
        model = ObjType
        exclude = ['user']
        labels = {
            'typename': 'Nombre del tipo de objeto',
        }
        widgets = {
            'typename': forms.TextInput(attrs={'class': 'form-control'}),
        }