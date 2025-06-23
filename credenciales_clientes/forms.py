from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from cuenta.models import Municipio, Persona, Cliente, Direccion

class ClienteLoginForm(forms.Form):
    correo = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tu correo electrónico',
            'id': 'login-email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tu contraseña',
            'id': 'login-password'
        })
    )

class ClienteRegistroForm(forms.Form):
    nombre = forms.CharField(max_length=150, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Nombre'
    }))
    primer_apellido = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Primer apellido'
    }))
    segundo_apellido = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Segundo apellido (opcional)'
    }))
    correo = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Correo electrónico'
    }))
    numero_documento = forms.CharField(max_length=20, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Número de documento'
    }))
    telefono = forms.CharField(max_length=15, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Teléfono'
    }))
    departamento = forms.ChoiceField(choices=[], widget=forms.Select(attrs={
        'class': 'form-control',
        'id': 'reg-departamento'
    }))
    municipio = forms.ChoiceField(choices=[], widget=forms.Select(attrs={
        'class': 'form-control',
        'id': 'reg-municipio',
    }))
    calle = forms.CharField(max_length=255, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Dirección completa'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Contraseña'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Confirmar contraseña'
    }))
    terms = forms.BooleanField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from cuenta.models import Departamento
        self.fields['departamento'].choices = [('', 'Selecciona departamento')] + [
            (d.id, d.nombre) for d in Departamento.objects.all()
        ]
        self.fields['municipio'].choices = [(m.id, m.nombre) for m in Municipio.objects.all()]

    def clean_correo(self):
        correo = self.cleaned_data.get('correo')
        if Persona.objects.filter(correo=correo).exists():
            raise ValidationError('Este correo ya está registrado')
        return correo

    def clean_numero_documento(self):
        numero = self.cleaned_data.get('numero_documento')
        if Cliente.objects.filter(numero_documento=numero).exists():
            raise ValidationError('Este documento ya está registrado')
        return numero

    def clean(self):
        data = super().clean()
        if data.get('password') != data.get('confirm_password'):
            raise ValidationError('Las contraseñas no coinciden')
        return data

    def save(self):
        municipio_id = self.cleaned_data['municipio']
        municipio = Municipio.objects.get(id=municipio_id)
        direccion = Direccion.objects.create(
            calle=self.cleaned_data['calle'],
            municipio=municipio
        )
        persona = Persona.objects.create(
            nombre=self.cleaned_data['nombre'],
            primer_apellido=self.cleaned_data['primer_apellido'],
            segundo_apellido=self.cleaned_data.get('segundo_apellido', ''),
            correo=self.cleaned_data['correo']
        )
        cliente = Cliente.objects.create(
            persona=persona,
            numero_documento=self.cleaned_data['numero_documento'],
            telefono=self.cleaned_data['telefono'],
            direccion=direccion,
            contraseña=make_password(self.cleaned_data['password'])
        )
        return cliente