# -*- coding: utf-8 -*-
from django.forms import models as model_forms
from django.shortcuts import render, render_to_response, RequestContext, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User, Group
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.contrib import auth
from django.views.generic import (
    CreateView, UpdateView, ListView, DetailView,
    DeleteView
)
from django.views.generic import ListView
from django.core.urlresolvers import reverse_lazy

from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse
import datetime
from django.core.mail import send_mail, BadHeaderError
from django.forms import ModelForm
from django import forms
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.formtools.wizard.forms import ManagementForm
from django.utils.datastructures import SortedDict
from django.utils import six
import copy
from django.core.exceptions import ValidationError
from django.template.response import TemplateResponse
#-------------------------------------------------------------------------------------------

from .models import EquipoTrabajo, Proyecto

class ProyectoCreateView(CreateView):
    model = Proyecto
    success_url = reverse_lazy('konekata')
    #Gestion = Group.objects.get(name="Gestión Interna").user_set.all()
    #if request.user in gestion:
    #def get_form_class(self):
    #    return model_forms.modelform_factory(
    #        self.model,
    #        exclude=[
    #            'aprobado',
    #            'revisado',
    #            'solicitante',
    #            #'enviado',
    #            'aprobacion_a',
    #            'aprobacion_b',
    #            'aprobado_por',
    #            #'fecha_creacion',
    #            'fecha_solicitud',
    #            'enviado',
    #        ]
    #    )
    #
    def form_valid(self, form):
        if form.is_valid():
            
            proyectos = Proyecto.objects.all()
            print form.instance.nombre
            for p in proyectos:
                if p.nombre == form.instance.nombre:
                    return self.render_to_response(self.get_context_data(form = form, existe = True))
                    #raise ValidationError('Nombre ya existe')
            if form.instance.nombre != '' and form.instance.descripcion != '':
                super(ProyectoCreateView, self).form_valid(form)
                return redirect('/proyectos/')
            else:
                raise Http404();
            #return super(PermisoCreateView, self).form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))
    
    def get_context_data(self, **kwargs):
        
        presidencia = Group.objects.get(name="Presidencia").user_set.all()
        if self.request.user in presidencia:

            print kwargs['form']
            context = super(ProyectoCreateView, self).get_context_data(**kwargs)
            return context
    
    
    
class ProyectoListView(ListView):
    model = Proyecto
    success_url = reverse_lazy('konekata')
    
    def get(self, request, *args, **kwargs):
        super(ProyectoListView, self).get(request, *args, **kwargs)
        presidencia = Group.objects.get(name="Presidencia").user_set.all()
        object_list = []
        queryset = Proyecto.objects.all()
        
        for obj in queryset:
            object_list.append(obj)

        
        context = self.get_context_data(object_list=queryset)
        
        if self.request.user in presidencia:
            context['presidencia'] = True
        
        
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        
        context = super(ProyectoListView, self).get_context_data(**kwargs)
        presidencia = Group.objects.get(name="Presidencia").user_set.all()
        if self.request.user in presidencia:
            
            context['presidencia'] = True
        
        return context

class ProyectoDetailView(DetailView):
    
    model = Proyecto
    
class ProyectoDeleteView(DeleteView):
    model = Proyecto
    success_url = reverse_lazy('konekata')
    
    
    def delete(self, request, *args, **kwargs):
        presidencia = Group.objects.get(name="Presidencia").user_set.all()
        
        if self.request.user in presidencia:
            #print u'presidencia'
            self.object = self.get_object()
            success_url = self.get_success_url()
            self.object.delete()
            return HttpResponseRedirect(success_url)
        else:
            raise Http404();

    def get(self, request, *args, **kwargs):
        
        self.object = self.get_object()
        presidencia = Group.objects.get(name="Presidencia").user_set.all()
        if self.request.user in presidencia:
            context = self.get_context_data(object=self.object)
            return self.render_to_response(context)
        else:
            raise Http404();
    
    def form_valid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """
        if request.is_valid():
            return HttpResponseRedirect(self.get_success_url())
        else:
            raise Http404();
    
    
class ProyectoUpdateView(UpdateView):
    model = Proyecto
    success_url = reverse_lazy('proyecto-listar')
    
    
    #def get_form_class(self):
    #    return model_forms.modelform_factory(
    #        self.model,
    #        exclude=[
    #
    #        ]
    #    )
    
    def form_valid(self, form):
        if form.is_valid():
            proyecto = Proyecto.objects.exclude(id = self.object.pk)
            #if equipo.nombre existe
            
            for p in proyecto:
                if form.instance.nombre == p.nombre:
                    return self.render_to_response(self.get_context_data(form=form, existe=True))
            presidencia = Group.objects.get(name="Presidencia").user_set.all()
            
            if self.request.user in presidencia:
                return super(ProyectoUpdateView, self).form_valid(form)
                #return reverse('proyecto-listar')
                
            else:
                raise Http404();
        else:
            return self.render_to_response(self.get_context_data(form=form))    
        
    
    #def get_form(self, form_class):
    #    form = super(ProyectoCreateView, self).get_form(form_class)
    #    return form
    def get_context_data(self, **kwargs):
        
        proyecto = Proyecto.objects.get(id = self.object.pk)
            #if equipo.nombre existe
        presidencia = Group.objects.get(name="Presidencia").user_set.all()
        
        if self.request.user in presidencia:
            print u'**************************'
            #context = super(ProyectoCreateView, self).get_context_data(**kwargs)
            context = super(ProyectoUpdateView, self).get_context_data(**kwargs)
        else:
            
            raise Http404();
        
        return context

            #})
    
    def get_success_url(self):
        return reverse('proyecto-listar')
    
#_______________________________________________________

class EquipoTrabajoCreateView(CreateView):
    template_name = "equipo_trabajo/crear_equipo.html"
    model = EquipoTrabajo
    success_url = reverse_lazy('konekata')
    
    
    #Gestion = Group.objects.get(name="Gestión Interna").user_set.all()
    #if request.user in gestion:
    #def get_form_class(self):
    #    return model_forms.modelform_factory(
    #        self.model,
    #        exclude=[
    #            'aprobado',
    #            'revisado',
    #            'solicitante',
    #            #'enviado',
    #            'aprobacion_a',
    #            'aprobacion_b',
    #            'aprobado_por',
    #            #'fecha_creacion',
    #            'fecha_solicitud',
    #            'enviado',
    #        ]
    #    )
    #
    def form_valid(self, form):
        if form.is_valid():
            equipo = EquipoTrabajo.objects.all()
            
            for e in equipo:    
                if form.instance.nombre == e.nombre:
                    return self.render_to_response(self.get_context_data(form=form, existe=True))
            if (
                form.instance.nombre != '' and form.instance.director_proyecto != ''
            ):
                super(EquipoTrabajoCreateView, self).form_valid(form)
                return redirect('/proyectos/')
            else:
                raise Http404();
            #return super(PermisoCreateView, self).form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))
    
    def get_context_data(self, **kwargs):
        
        presidencia = Group.objects.get(name="Presidencia").user_set.all()
        if self.request.user in presidencia:
            
            #if self.request.POST:
                #inicio = request.POST.get('f_inicio')
                #fin = request.POST.get('f_fin')
                #print redirequest.POST.get('f_fin')
            context = super(EquipoTrabajoCreateView, self).get_context_data(**kwargs)
            #else:
            #    return Http404
            return context
    

class EquipoTrabajoListView(ListView):
    template_name = "equipo_trabajo/equipo_listar.html"
    model = EquipoTrabajo
    
    def get(self, request, *args, **kwargs):
        super(EquipoTrabajoListView, self).get(request, *args, **kwargs)
        presidencia = Group.objects.get(name="Presidencia").user_set.all()
        queryset = EquipoTrabajo.objects.all()
        

        context = self.get_context_data(object_list=queryset)
        
        if self.request.user in presidencia:
            context['presidencia'] = True
        
        
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        
        context = super(EquipoTrabajoListView, self).get_context_data(**kwargs)
        presidencia = Group.objects.get(name="Presidencia").user_set.all()
        if self.request.user in presidencia:
            
            context['presidencia'] = True
        
        return context
    
class EquipoTrabajoDetailView(DetailView):
    model = EquipoTrabajo
    template_name = "equipo_trabajo/equipotrabajo_detail.html"

class EquipoTrabajoUpdateView(UpdateView):
    model = EquipoTrabajo
    template_name = "equipo_trabajo/crear_equipo.html"
    success_url = reverse_lazy('equipo-listar')
    
    
    def form_valid(self, form):
        if form.is_valid():
            
            #if equipo.nombre existe
            presidencia = Group.objects.get(name="Presidencia").user_set.all()
            equipo = EquipoTrabajo.objects.exclude(id = self.object.pk)
            for p in equipo:
                if p.nombre == form.instance.nombre:
                    return self.render_to_response(self.get_context_data(form=form, existe= True))
            if self.request.user in presidencia:
                return super(EquipoTrabajoUpdateView, self).form_valid(form)
            else:
                raise Http404();
        else:
            
            return self.render_to_response(self.get_context_data(form=form))
        return reverse('equipo-listar')
    
    #def get_form(self, form_class):
    #    form = super(ProyectoCreateView, self).get_form(form_class)
    #    return form
    def get_context_data(self, **kwargs):
        print self.object.pk
        proyecto = EquipoTrabajo.objects.get(id = self.object.pk)
        presidencia = Group.objects.get(name="Presidencia").user_set.all()
        
        if self.request.user in presidencia:
            context = super(EquipoTrabajoUpdateView, self).get_context_data(**kwargs)
        else:
            
            raise Http404();
        
        return context

            #})
    
    def get_success_url(self):
        return reverse('equipo-listar')
    
    
class EquipoTrabajoDeleteView(DeleteView):
    model = EquipoTrabajo
    template_name = "equipo_trabajo/equipotrabajo_confirm_delete.html"
    success_url = reverse_lazy('konekata')
    

    def delete(self, request, *args, **kwargs):
        """
        Calls the delete() method on the fetched object and then
        redirects to the success URL.
        """
        #print request
        #if request.is_valid():
        #print u'ppppppppppppppppppp'
        presidencia = Group.objects.get(name="Presidencia").user_set.all()
        
        if self.request.user in presidencia:
            #print u'presidencia'
            self.object = self.get_object()
            success_url = self.get_success_url()
            self.object.delete()
            return HttpResponseRedirect(success_url)
            #return super(EquipoTrabajoDeleteView, self).form_valid(form)
        else:
            raise Http404();
        #else:
            #print u'doble-esle'
        

    def get(self, request, *args, **kwargs):
        
        self.object = self.get_object()
        presidencia = Group.objects.get(name="Presidencia").user_set.all()
        if self.request.user in presidencia:
            context = self.get_context_data(object=self.object)
            return self.render_to_response(context)
        else:
            raise Http404();
    
    def form_valid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """
        if request.is_valid():
            return HttpResponseRedirect(self.get_success_url())
        else:
            raise Http404();

    #def form_invalid(self, form):
    #    """
    #    If the form is invalid, re-render the context data with the
    #    data-filled form and errors.
    #    """
    #    return self.render_to_response(self.get_context_data(form=form))
    #def form_valid(self, form):
    #    print u'vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv'
    #    if form.is_valid():
    #        print u'ppppppppppppppppppp'
    #        presidencia = Group.objects.get(name="Presidencia").user_set.all()
    #        
    #        if self.request.user in presidencia:
    #            print u'presidencia'
    #            return super(EquipoTrabajoDeleteView, self).form_valid(form)
    #        else:
    #            print u'else'
    #            return Http404;
    #    else:
    #        print u'doble-esle'
    #        
    #        return self.render_to_response(self.get_context_data(form=form))
    #    return reverse('equipo-listar')
    