from django.contrib.auth.hashers import make_password
from django.forms import ModelForm, EmailInput, PasswordInput, TextInput
from django import forms
from gestion_empleados.models import Empleado



class EmpleadoEditarForm(forms.ModelForm):
    contraseña = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False
    )
    confirmar_contraseña = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Confirmar Contraseña",
        required=False
    )

    class Meta:
        model = Empleado
        fields = ['tipo_usuario']
        widgets = {
            'tipo_usuario': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        contraseña = cleaned_data.get("contraseña")
        confirmar_contraseña = cleaned_data.get("confirmar_contraseña")

        if contraseña or confirmar_contraseña:
            if contraseña != confirmar_contraseña:
                self.add_error('confirmar_contraseña', "Las contraseñas no coinciden")

        return cleaned_data

    def save(self, commit=True):
        empleado = super().save(commit=False)
        if self.cleaned_data['contraseña']:  # Solo actualizar contraseña si se proporcionó una nueva
            empleado.contraseña = make_password(self.cleaned_data['contraseña'])
        if commit:
            empleado.save()
        return empleado