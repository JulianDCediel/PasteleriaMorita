from django.forms import ModelForm, inlineformset_factory

from gestion_productos.models import Producto, PrecioProducto
from django import forms


class ProductoBaseForm(ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'imagen', 'categoria']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej. Pastel de Chocolate'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-control'
            }),
            'imagen': forms.FileInput(attrs={
                'class': 'form-control'
            })
        }

    def clean(self):
        cleaned_data = super().clean()
        imagen = cleaned_data.get('imagen')
        nombre = cleaned_data.get('nombre')
        categoria = cleaned_data.get('categoria')

        # Validación de tamaño de imagen
        if imagen and imagen.size > 2 * 1024 * 1024:  # 2MB
            self.add_error('imagen', 'La imagen no puede superar los 2MB')

        # Validación de nombre único por categoría
        if nombre and categoria:
            queryset = Producto.objects.filter(
                nombre__iexact=nombre,
                categoria=categoria
            )
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                self.add_error('nombre', 'Ya existe un producto con este nombre en la categoría seleccionada')

        return cleaned_data

    def save(self, commit=True):
        producto = super().save(commit=False)
        producto.nombre = producto.nombre.title()
        if commit:
            producto.save()
        return producto

class PrecioProductoForm(ModelForm):
    class Meta:
        model = PrecioProducto
        fields = ['presentacion', 'precio']
        widgets = {
            'presentacion': forms.Select(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01'
            })
        }

    def clean_precio(self):
        precio = self.cleaned_data.get('precio')
        if precio <= 0:
            raise forms.ValidationError("El precio debe ser mayor a cero")
        return precio

# Formset para manejar múltiples precios
PrecioProductoFormSet = inlineformset_factory(
    Producto,
    PrecioProducto,
    form=PrecioProductoForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True
)