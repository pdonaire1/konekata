# -*- coding: utf-8 -*-
from datetime import datetime
from django.db import models
from django.core.validators import MaxLengthValidator
from django.contrib.auth.models import User
from django import forms
from models import Entrada


from django.conf import settings
from django.core.files.storage import FileSystemStorage
import os


class MarcarEntradaForm(forms.ModelForm):
    class Meta:
        model = Entrada
        #file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'inicio/static/anexos'))
        fields = ['anexo_usuario']#,'anexos']
        #widgets = {
        #    'inicio': forms.DateInput(attrs={
        #        'id': 'inicio',
        #    }, format = '%Y-%m-%d'),
        #    'fin': forms.DateInput(attrs={
        #        'id': 'fin'
        #    }, format = '%Y-%m-%d'),
        #}
    
