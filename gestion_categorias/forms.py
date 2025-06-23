from django import forms
from django.core.exceptions import ValidationError

from gestion_productos.models import Categoria


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'imagen']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la categoría'
            }),
            'imagen': forms.FileInput(attrs={
                'class': 'form-control'
            })
        }
        labels = {
            'nombre': 'Nombre de la categoría',
        }

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        if Categoria.objects.filter(nombre__iexact=nombre).exists():
            raise ValidationError('Ya existe una categoría con este nombre.')
        return nombre


class CategoriaEditarForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'imagen']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la categoría'
            }),
            'imagen': forms.FileInput(attrs={
                'class': 'form-control'
            })
        }
        labels = {
            'nombre': 'Nombre de la categoría',
        }

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        # Excluimos la instancia actual de la verificación cuando estamos editando
        if self.instance.pk:
            if Categoria.objects.filter(nombre__iexact=nombre).exclude(pk=self.instance.pk).exists():
                raise ValidationError('Ya existe una categoría con este nombre.')
        else:
            if Categoria.objects.filter(nombre__iexact=nombre).exists():
                raise ValidationError('Ya existe una categoría con este nombre.')
        return nombre