from django import forms
from django.forms import ModelForm
from .models import Objects, PlaceLabel, ObjType, BoxLabel, Room

class CreateObjForm(forms.ModelForm):
    class Meta:
        model = Objects
        exclude = ['user','datereg']
        labels = {
            'name': 'Nombre del objeto',
            'description': 'Descripción',
            'label': 'Tipo de objeto',
            'placelabel': 'Lugar',
            'boxlabel': 'Cajón (opcional)',
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
            'boxlabel': forms.Select(attrs={'class': 'form-select'}),
            'important': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'whoIsIt': forms.TextInput(attrs={'class': 'form-control'}),
            'isInPlace': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['label'].queryset = ObjType.objects.filter(user=user)
            self.fields['placelabel'].queryset = PlaceLabel.objects.filter(user=user)
            self.fields['boxlabel'].queryset = BoxLabel.objects.filter(user=user)
            self.fields['boxlabel'].required = False  # que sea opcional




class CreatePlaceForm(forms.ModelForm):
    class Meta:
        model = PlaceLabel
        fields = ['name', 'description','room']
        labels = {'name': 'Nombre del lugar/mueble', 'room': 'Habitación', 'description': 'Descripción'}
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'room': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['room'].queryset = Room.objects.all()

class CreateBoxForm(forms.ModelForm):
    class Meta:
        model = BoxLabel
        fields = ['place']
        labels = {
            'place': 'En qué lugar está el cajón',
        }
        widgets = {
            'place': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # extraer usuario
        super().__init__(*args, **kwargs)
        if user:
            # Filtrar solo los lugares de este usuario
            self.fields['place'].queryset = PlaceLabel.objects.filter(user=user)

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

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['name']
        labels = {'name': 'Nombre de la habitación'}
        widgets = {'name': forms.TextInput(attrs={'class': 'form-control'})}
