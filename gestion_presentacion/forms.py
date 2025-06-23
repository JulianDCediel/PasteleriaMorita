from django import forms

from gestion_productos.models import Presentacion


class PresentacionForm(forms.ModelForm):
    class Meta:
        model = Presentacion
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la presentacion'
            }),
        }
        labels = {
            'nombre': 'Nombre de la presentacion',
        }

class PresentacionEditarForm(forms.ModelForm):
    class Meta:
        model = Presentacion
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la presentacion'
            }),
        }
        labels = {
            'nombre': 'Nombre de la presentacion',
        }