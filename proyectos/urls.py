# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from permisos.views import (
    PermisoCreateView, PermisoUpdateView, PermisoDetailView,
    PermisoListView, PermisoDeleteView
)
from permisos.views import *
#from .views import por_fecha_inicio

from . import views
from django_filters.views import FilterView
from django.forms import ModelForm
from django import forms
from permisos.views import PermisoCrearWizard

from .models import Proyecto, EquipoTrabajo
from .views import (
    ProyectoCreateView,
    ProyectoListView,
    ProyectoDetailView,
    ProyectoDeleteView,
    ProyectoUpdateView,
    EquipoTrabajoCreateView,
    EquipoTrabajoListView,
    EquipoTrabajoDetailView,
    EquipoTrabajoUpdateView,
    EquipoTrabajoDeleteView,
)

urlpatterns = patterns('',
    
    
  
    
    url(r'^crear/$', login_required(ProyectoCreateView.as_view()),
        name='proyecto-crear'),
    
    url(r'^nuevo_equipo/$', login_required(EquipoTrabajoCreateView.as_view()),
        name='proyecto-crear'),    
     
    url(r'^listar/$', login_required(ProyectoListView.as_view()),
        name='proyecto-listar'),
    url(r'^listar_equipo/$', login_required(EquipoTrabajoListView.as_view()),
        name='equipo-listar'),
        
    url(r'^editar_equipo/(?P<pk>\w+)/$', login_required(EquipoTrabajoUpdateView.as_view()),
        name='equipo-listar'),
    url(r'^editar/(?P<pk>\w+)/$', login_required(ProyectoUpdateView.as_view()),
        name='equipo-listar'),
        
    url(r'^detalle/(?P<pk>\w+)/$', login_required(ProyectoDetailView.as_view()),
        name='proyecto-detalle'),
    url(r'^detalle_equipo/(?P<pk>\w+)/$', login_required(EquipoTrabajoDetailView.as_view()),
        name='equipo-detalle'),
    #    
    url(r'^eliminar/(?P<pk>\w+)/$', login_required(ProyectoDeleteView.as_view()),
        name='proyecto-eliminar'),
    url(r'^eliminar_equipo/(?P<pk>\w+)/$', login_required(EquipoTrabajoDeleteView.as_view()),
        name='proyecto-eliminar'),
        

)