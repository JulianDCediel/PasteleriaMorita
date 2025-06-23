from django import forms
from django.core.exceptions import ValidationError
from cuenta.models import Cliente, Persona, Direccion

class EditarClienteForm(forms.Form):
    nombre = forms.CharField(max_length=50, required=True)
    primer_apellido = forms.CharField(max_length=50, required=True)
    segundo_apellido = forms.CharField(max_length=50, required=False)
    correo = forms.EmailField(required=True)
    telefono = forms.CharField(max_length=15, required=True)
    departamento = forms.IntegerField(required=True)
    municipio = forms.IntegerField(required=True)
    calle = forms.CharField(max_length=100, required=True)
    password = forms.CharField(max_length=128, required=False, widget=forms.PasswordInput)
    confirm_password = forms.CharField(max_length=128, required=False, widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password or confirm_password:
            if password != confirm_password:
                raise ValidationError("Las contraseñas no coinciden")

        return cleaned_data

