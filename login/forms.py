from django.contrib.auth.hashers import make_password
from django.forms import ModelForm, EmailInput, PasswordInput, TextInput
from django import forms
from gestion_empleados.models import Empleado, Persona



class LoginEmpleadoForm(forms.Form):
    correo = forms.EmailField(label="Correo", max_length=100)
    contraseña = forms.CharField(label="Contraseña", widget=forms.PasswordInput)

class PersonaForm(ModelForm):
    class Meta:
        model = Persona
        fields = ['nombre', 'primer_apellido', 'segundo_apellido', 'correo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'primer_apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'segundo_apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class EmpleadoForm(forms.ModelForm):
    contraseña = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirmar_contraseña = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Confirmar Contraseña"
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

        if contraseña and confirmar_contraseña and contraseña != confirmar_contraseña:
            self.add_error('confirmar_contraseña', "Las contraseñas no coinciden")

        return cleaned_data

    def save(self, commit=True):
        empleado = super().save(commit=False)
        empleado.contraseña = make_password(self.cleaned_data['contraseña'])
        if commit:
            empleado.save()
        return empleado