# -*- coding: utf-8 -*-

import django_filters
from django.forms.widgets import CheckboxInput, NullBooleanSelect
from django.forms.widgets import DateInput
from django_filters.filters import Filter
from .models import Permiso

#class CustomDateRangeFilter(Filter):
#    field_class = DateRangeField
#    def filter(self, qs, value):
#        if value:
#            return qs.filter(**{'%s__range' % self.name: (value.start, value.stop)})
#        return qs



class PermisoFilterSet(django_filters.FilterSet):
    class Meta:
        model = Permiso
        fields = [
            'solicitante',
            'fecha_solicitud',
            'inicio',
            'fin',
            #'suplente',
            'revisado',
            'aprobado',
            #'aprobado_a',
            #'aprobado_b',
            #'aprobado_director',
            #'aprobado'
            ]

    def __init__(self, *args, **kwargs):
        super(PermisoFilterSet, self).__init__(*args, **kwargs)
        self.filters['aprobado'].field.widget.widgets = (
            NullBooleanSelect(attrs={'class': 'ok'}),
        )
        #self.filters['inicio'].field.widget.widgets = (
        #    CheckboxInput(attrs={'class': 'checkbox'}),
        #    DateInput(attrs={'class': 'date'})
        #)

class Permisos_usuarioFilterSet(django_filters.FilterSet):
    class Meta:
        model = Permiso
        
        fields = [
            'fecha_solicitud',
            'inicio',
            'fin',
            'revisado',
            #'aprobado_por',
            'aprobado',
            ]

class Permisos_ausentesFilterSet(django_filters.FilterSet):
    class Meta:
        model = Permiso
        
        fields = [
            #'fecha_solicitud',
            #'inicio',
            #'fin',
            #'suplente',
            #'revisado',
            'aprobado_por',
            #'aprobado_director',
            'aprobado'
            ]
        
class PermisoSinLeerFilterSet(django_filters.FilterSet):
    class Meta:
        model = Permiso
        fields = ['solicitante']


class PermisoLeidasFilterSet(django_filters.FilterSet):
    class Meta:
        model = Permiso
        fields = ['aprobado_por']


class Permisos_suplenteFilterSet(django_filters.FilterSet):
    class Meta:
        model = Permiso
        
        fields = [
            'solicitante',
            'suplente',
            'fecha_solicitud',
            'inicio',
            'fin',
            ]

#Instalation
#
#Use pip/easy_install
#
#    pip install django-daterange-filter
#
#In your models.py
#
#    from daterange_filter.fields import DateRangeField
#
#    class Example(models.Model):
#
#        bar = DateRangeField(null=True, blank=True, etc...) bar.daterange_filter = True
#
