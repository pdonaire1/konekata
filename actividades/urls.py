# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from .views import (
    ActividadCreateView, ActividadListView, ActividadUpdateView, ActividadPerticiparUpdateView,
    ActividadDetailView, MarcarEntrada, ActividadInscritosDetalle, ActividadDeleteView
)

from . import views
from django_filters.views import FilterView
from django.forms import ModelForm
from django import forms


#from permisos.views import *
#from .views import por_fecha_inicio

from . import views
import konekata.urls
#from django.conf.urls import patterns, url import views

urlpatterns = patterns('',
    url(r'^crear/$', login_required(ActividadCreateView.as_view()),
        name='crear-actividad'),

    url(r'^listar/$', login_required(ActividadListView.as_view()),
        name='listar-actividad'),

    url(r'^editar/(?P<pk>\d+)/$', login_required(ActividadUpdateView.as_view()),
        name='editar-actividad'),

    url(r'participar/(?P<pk>\d+)/', login_required(ActividadPerticiparUpdateView.as_view())),

    url(r'detalle/(?P<pk>\d+)/', login_required(
            ActividadDetailView#.as_view()
        )
    ),
    url(r'eliminar/(?P<pk>\d+)/', login_required(
            ActividadDeleteView.as_view()
        ),
        name='eliminar-actividad'
    ),

    url(r'marcar/', login_required(MarcarEntrada)),
    #url(r'ver-inscritos/(?P<pk>\d+)/', login_required(ActividadVerInscritos.as_view())),
    #url(r'^crear/$', login_required(ProyectoCreateView.as_view()),
    #name='proyecto-crear'),
    url(r'ajax-detalle-inscritos/$', login_required(
        ActividadInscritosDetalle.as_view()
    )),


)

