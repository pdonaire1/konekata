# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from .views import (
    PermisoCreateView, PermisoUpdateView, PermisoDetailView,
    PermisoListView, PermisoDeleteView, BusquedaAjaxView,
    ProcesarDependienteUpdateView, ProcesarTalentoHumano,
    ProcesarPresidencia, ProcesarDireccionEjecutiva,
    ProcesarDireccionGestion, ValidarFechas
)
from permisos.views import *
#from .views import por_fecha_inicio

from . import views
from django_filters.views import FilterView
from django.forms import ModelForm
from django import forms

from forms import PermisoCrearForm1, PermisoCrearForm2
from views import PermisoCrearWizard
from forms import PermisoCrearForm1, PermisoCrearForm2
urlpatterns = patterns('',
    
    
    
    url(r'^crear_form/$',
        login_required(PermisoCrearWizard.as_view([PermisoCrearForm1, PermisoCrearForm2]))
    ),
    
    #url(r'^crear1/$',
    #    views.PermisoCreate1,  
    #),
    
    url(r'^observaciones/(?P<pk>\d+)/$',
        views.VerObservaciones,
    ),
    
    url(r'^crear/$', login_required(PermisoCreateView.as_view()),
        name='permiso-crear'),
        
    
    url(r'^editar/(?P<pk>\d+)/$', login_required(PermisoUpdateView.as_view()),
        name='permiso_edit'),
    
    url(r'^procesar-dependiente/(?P<pk>\d+)/$', ProcesarDependienteUpdateView,
        name='procesar-dependiente'
    ),
    
    url(r'^procesar-talento/(?P<pk>\d+)/$', ProcesarTalentoHumano,
        name='procesar-talento'
    ),
    
    url(r'^procesar-presidencia/(?P<pk>\d+)/$', ProcesarPresidencia,
        name='procesar-presidencia'
    ),
    
    url(r'^procesar-direccion-ejecutiva/(?P<pk>\d+)/$', ProcesarDireccionEjecutiva,
        name='procesar-direccion-ejecutiva'
    ),
    
    url(r'^procesar-direccion-gestion/(?P<pk>\d+)/$', ProcesarDireccionGestion,
        name='procesar-direccion-gestion'
    ),
    
    #url(r'^procesar-dependiente/(?P<pk>\d+)/$', login_required(ProcesarDependienteUpdateView.as_view()),
    #    name='procesar-dependiente'),
    #
    
    
    
    ## este es listar talento humano
    url(r'^listar/$', login_required(PermisoListView.as_view()),
        name='permiso-listar'),
    
    url(r'^listar-dependientes/$', login_required(PermisoDependienteListView.as_view()),
        name='permiso-listar-suplentes'),
    
    url(r'^listar-direccion/$', login_required(PermisoDireccionEjecutivaListView.as_view()),
        name='permiso-direccion'),
    
    url(r'^listar-direccion-gestion/$', login_required(PermisoDireccionGestionListView.as_view()),
        name='permiso-direccion-gestion'),
    
    url(r'^listar-presidencia/$', login_required(PermisoPresidenciaListView.as_view()),
        name='permiso-presidencia'),    
    
    
    url(r'^listar-permisos/$', login_required(PermisosDeUsuarioListView.as_view()),
        name='listar-por-usuarios'),
    
    url(r'^listar-ausentes/$', login_required(AusentesListView.as_view()),
        name='listar-ausentes'),    
        
        
    url(r'^detalle/(?P<pk>\w+)/$', login_required(PermisoDetailView.as_view()),
        name='permiso_detalle'),
        
        
    url(r'^eliminar/(?P<pk>\w+)/$', login_required(PermisoDeleteView.as_view()),
        name='permiso-eliminar'),
        
    
    url(r'^procesar/(?P<pk>\d+)/$',
        views.procesar,
    ),
    
    url(r'^busqueda_ajax/$', BusquedaAjaxView.as_view()),

    url(r'^validar_fecha/$',
        ValidarFechas.as_view()
    ),
    
    
    
    #url (r'^aprobar/$',
    #    views.aprobar,
    #),
    
    
    #url(r'^listar/solicitante/(?P<solicitante>\w+)$', login_required(PermisoListView.por_solicitante('admin')),
    #    name = 'por-solicitante'),
    
    #url(r'^enviar/$', login_required(permiso_enviar)),
    #url(r'^detalle_pdf/(?P<pk>\w+)/$', login_required(permiso_detail_pdf),
    #    name='permiso-pdf'),
    #url(r'^detalles_pdf/$', login_required(permisos_detail_pdf),
    #    name='permisos-pdf'),
    
    
    #---------------------------------------------------------------------------------
    #---------------------------------------------------------------------------------
    #---------------------------------------------------------------------------------
    #url(r'^editar/(?P<pk>\d+)/$', login_required(views.editar),
    #    name='permiso_edit'),
    
    #url(r'^procesadas/$',
    #    views.leidas,
    #    ),#url(r'^listar-inicio/([0-9]{4})/([0-9]{2})/([0-9]+)/$',
    #views.por_fecha_inicio,
    #name = 'por-inicio'
    #),
        #url(r'^sin-leer/$',
    #    views.sin_leer,
    #    ),
    #url(
    #  r'^sin_leer/$', login_required(SinLeerListView.as_view())  ,
    #  name = 'sin-leer'
    #),
    #url(
    #  r'^leidas/$', login_required(LeidasListView.as_view())  ,
    #  name = 'leidas'
    #),
    #url(r'^listarpropias/$', login_required(PermisoUsuarioListView.as_view()),
    #    name='permiso-listar-usuario'),
    #url(r'^listarecibidas/$', login_required(PermisoRecibidaListView.as_view()),
    #    name='permiso-listar-recibida'),
     #url(r'^listar-inicio/(?P<fs>\w+)/$',
    #    views.por_fecha_inicio,
    #    name = 'por-inicio'
    #    )
)