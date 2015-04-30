# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from .views import (
    UsuarioUpdateView, recuperar_password, cambiar_password,
    
)
#from permisos.views import *
#from .views import por_fecha_inicio

from . import views
import konekata.urls
#from django.conf.urls import patterns, url import views


urlpatterns = patterns('',                       
    url(r'^editar_usuario/(?P<pk>\d+)/$', login_required(UsuarioUpdateView.as_view()),
        name='editar-usuario'),
    url(r'^recuperar-password/$', recuperar_password,
        name='recuperar-password'),
    url(r'^cambiar-password/(?P<pk>\d+)/$', login_required(cambiar_password),
        name='cambiar-password'),
    
    #url(r'^password_change/$',  # hijack password_change's url
    #    'django.contrib.auth.views.password_change',
    #    {'password_change_form': AdminPasswordChangeForm},
    #    name="password_change"),
    #url(r'^accounts/', include('django.contrib.auth.urls')),
    #
    #url(r'^$', views.IndexView.as_view(), name='index'),
    #               url(r'^(?P<pk>\d+)/$', views.DetailView.as_view(), name='detail'),
    #               url(r'^(?P<pk>\d+)/results/$',     views.ResultsView.as_view(),name='results'),
    #               url(r'^(?P<poll_id>\d+)/vote/$', 'polls.views.vote', name='votes'),
    #               url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
    #                                {'document_root':       '/home/bri6ko/DjangoProjects/django1.6/PoolsDjangoProject/'}),
    
                       
)

