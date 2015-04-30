# -*- coding: utf-8 -*-
from datetime import datetime
from django.db import models
from django.core.validators import MaxLengthValidator
from django.contrib.auth.models import User
from django import forms
from models import Permiso, Observaciones


from django.conf import settings
from django.core.files.storage import FileSystemStorage
import os


class PermisoCrearForm1(forms.ModelForm):
    class Meta:
        model = Permiso
        file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'inicio/static/anexos'))
        fields = ['inicio', 'fin']#,'anexos']
        widgets = {
            'inicio': forms.DateInput(attrs={
                'id': 'inicio',
            }, format = '%Y-%m-%d'),
            'fin': forms.DateInput(attrs={
                'id': 'fin'
            }, format = '%Y-%m-%d'),
        }
    

class PermisoCrearForm2(forms.ModelForm):
    class Meta:
        model = Permiso
        fields = [
            'observacion',
            'suplente',
            'anexo_permiso'
            #'equipo_trabajo',
            #'solicitante',
            #'fecha_creacion',
            #'fecha_solicitud',
            #'revisado',
            #'aprobado_por',
            #'aprobacion_a',
            #'aprobacion_b',
            #'aprobado',
            #'enviado',
            
        ]


class ObservacionesForm(forms.Form):

    CHAR_CHOICES = (
        ('Trabajador','Trabajador'),
        ('Talento','Talento Humano'),
        ('Direccion', 'Dirección Ejecutiva'),
        ('Presidencia', 'Presidencia'),
    )
    para = forms.CharField(
        max_length = 12,
        widget=forms.Select(choices=CHAR_CHOICES)
    )
    observacion = forms.TextInput()#.CharField(max_length=5000)
    
    """
    class Media(object):
        js = formset_media_js + (
            # Other form media here
        )
    """
    
    
    """
    def __unicode__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(ObservacionesForm, self).__unicode__(*args, **kwargs)
    """
    