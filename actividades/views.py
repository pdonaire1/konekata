# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.forms import models as model_forms
from django.contrib.auth.models import User, Group
from django.views.generic import (
    CreateView, UpdateView, ListView, DetailView,
    DeleteView, TemplateView
)
from actividades.models import Actividad, Entrada
from django.shortcuts import redirect
import json
from .models import *
from django.db.models import Q
from django.core import serializers
from django.db.models import Q
from django.utils import timezone
from django.http import HttpResponse, Http404, HttpResponseRedirect
import os
from .forms import MarcarEntradaForm

class ActividadCreateView(CreateView):
    model = Actividad
    template_name="actividad/actividad1_form.html"
    success_url = reverse_lazy('actividad')

    def get_form_class(self):
        return model_forms.modelform_factory(
            self.model,
            exclude=[
                'fecha_ingreso',
            ]
        )

    def form_valid(self, form):

        if form.is_valid():
            actividad = Actividad.objects.all()
            for a in actividad:
                if form.instance.nombre == a.nombre:
                    return self.render_to_response(self.get_context_data(form=form, existe=True))

            comunicacion = Group.objects.get(name="Comunicación Social").user_set.all()
            if self.request.user in comunicacion:
                return super(ActividadCreateView, self).form_valid(form)
            else:
                raise Http404();
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):

        comunicacion = Group.objects.get(name="Comunicación Social").user_set.all()
        if self.request.user in comunicacion:
            context = super(ActividadCreateView, self).get_context_data(**kwargs)
        else:
            raise Http404();
        return context


    def get_success_url(self):
        return reverse('actividad')



class ActividadUpdateView(UpdateView):
    model = Actividad
    template_name = 'actividad/actividad1_form.html'
    success_url = reverse_lazy('actividad')

    def get_form_class(self):
        return model_forms.modelform_factory(
            self.model,
            exclude=[
                'fecha_ingreso',
            ]
        )

    def form_valid(self, form):
        if form.is_valid():
            actividad = Actividad.objects.exclude(id = self.object.pk)
            for a in actividad:
                if form.instance.nombre == a.nombre:
                    return self.render_to_response(self.get_context_data(form=form, existe=True))
            comunicacion = Group.objects.get(name="Comunicación Social").user_set.all()
            query = Actividad.objects.get(id = self.object.pk)
            if self.request.user in comunicacion and query.fecha_salida>timezone.now():
                return super(ActividadUpdateView, self).form_valid(form)
            else:
                raise Http404();
        else:
            return self.render_to_response(self.get_context_data(form=form))


    def get_context_data(self, **kwargs):
        comunicacion = Group.objects.get(name="Comunicación Social").user_set.all()
        actividad = Actividad.objects.get(id = self.object.pk)
        if self.request.user in comunicacion and actividad.fecha_salida>timezone.now():
            context = super(ActividadUpdateView, self).get_context_data(**kwargs)
            context['id_modelo'] = actividad.pk
        else:
            raise Http404();
        return context


    def get_success_url(self):
        return reverse('actividad')


#class ActividadDetailView(DetailView):
#    model = Actividad
#    template_name = "actividad/actividad_detalle.html"

def ActividadDetailView(request, pk):
    print request
    try:
        model = Actividad.objects.get(id = pk)
    except:
        raise Http404()
    usuarios = Entrada.objects.filter(actividad = model)
    
    #path_to_file = os.path.realpath('/media/anexos_actividad/BannerAutanaContab.jpg')
    #f = open(path_to_file, 'r')
    #print '******************'
    #print f
    #myfile = File(f)
    #response = HttpResponse(myfile, content_type='application/vnd.ms-excel')
    #response['Content-Disposition'] = 'attachment; filename=' + name
    #return response
    comunicacion = Group.objects.get(name="Comunicación Social").user_set.all()
    
    if request.user in comunicacion and model.fecha_salida > timezone.now():
        es_comunicacion = True
    else:
        es_comunicacion = False
    return render(request, 'actividad/actividad_detalle.html', {
        'object':model,
        'usuarios': usuarios,
        'comunicacion': es_comunicacion
    })



#from django.utils import simplejson
class ActividadInscritosDetalle(TemplateView):

    def get(self, request, *args, **kwargs):
        
        entradas = Entrada.objects.filter(
            actividad__id=self.request.GET['actividad'],
        )
        
        data = {}
        data['si'] = True
        for i in entradas:
            data[str(i.usuario)] = str(i.fecha_ingreso)
        try:
            print json.dumps(data)
            print u'bien'
        except (TypeError, ValueError) as err:
            print 'ERROR:', err
        #data = serializers.serialize(
        #    'json',
        #    entradas,
        #    fields=('usuario', 'fecha_ingreso',)
        #)
        #print data
        #return HttpResponse(data, mimetype='application/json')
        
        
        print u'aaaaaaaa'
        
        return HttpResponse(json.dumps(data), content_type="application/json")

        #return HttpResponse(json.dumps(data), content_type="application/json")
        #return HttpResponse(json.dumps(data), content_type="application/json")
        
        #return self.render_to_json_response(data)
        #return HttpResponse(simplejson.dumps(data), mimetype='application/json')
        





class ActividadPerticiparUpdateView(UpdateView):
    model = Actividad
    template_name = 'actividad/participar1_form.html'
    success_url = reverse_lazy('actividad')

    def get_form_class(self):
        return model_forms.modelform_factory(
            self.model,
            exclude=[
                'fecha_ingreso',
                'nombre',
                'fecha_salida',
                'fecha_fin',
                'fecha_ingreso',
                'informacion',
                'inscritos',
            ]
        )

    def form_valid(self, form):
        if form.is_valid():
            trabajador = Group.objects.get(name="Trabajador").user_set.all()
            if self.request.user in trabajador:
                actividad = Actividad.objects.get(id = self.object.pk)
                if self.request.user in actividad.inscritos.all():
                    if actividad.fecha_salida > timezone.now():
                        actividad.inscritos.remove(self.request.user)
                else:
                    usuario = User.objects.get(username = self.request.user)
                    actividad.inscritos.add(usuario)
                actividad.save()
                return super(ActividadPerticiparUpdateView, self).form_valid(form)
            else:
                raise Http404();
        else:
            return self.render_to_response(self.get_context_data(form=form))


    def get_context_data(self, **kwargs):
        trabajador = Group.objects.get(name="Trabajador").user_set.all()
        actividad = Actividad.objects.get(id = self.object.pk)#.values_list('inscritos')
        #print actividad.inscritos.exclude(pk=1)
        if self.request.user in trabajador and actividad.fecha_salida > timezone.now():
            context = super(ActividadPerticiparUpdateView, self).get_context_data(**kwargs)
            if self.request.user in actividad.inscritos.all():
                context['inscrito'] = True
        else:
            raise Http404();
        return context


    def get_success_url(self):
        return reverse('actividad')

class ActividadListView(ListView):
    model = Actividad
    template_name="actividad/actividad1_list.html"
    paginate_by = 7
    def get(self, request, *args, **kwargs):
        super(ActividadListView, self).get(request, *args, **kwargs)
        object_list = []
        queryset = Actividad.objects.all()
        context = self.get_context_data(object_list=queryset, ahora=timezone.now())
        #if self.request.user in queryset.inscritos.all():
        #    context['inscrito'] = True

        return self.render_to_response(context)


    def get_context_data(self, **kwargs):
        context = super(ActividadListView, self).get_context_data(**kwargs)
        return context
#
#
#class ActividadVerInscritos(ListView):
#    model = Actividad
#    template_name="actividad/actividad2_list.html"
#
#    def get(self, request, *args, **kwargs):
#
#        super(ActividadVerInscritos, self).get(request, *args, **kwargs)
#        #print u'0000000'
#        object_list = []
#        actividad = Actividad.objects.filter(
#            id = self.request.pk
#        )
#        queryset = actividad.inscritos.all()
#        context = self.get_context_data(object_list=queryset)
#        print queryset
#        #if self.request.user in queryset.inscritos.all():
#        #    context['inscrito'] = True
#
#        return self.render_to_response(context)


    def get_context_data(self, **kwargs):
        context = super(ActividadListView, self).get_context_data(**kwargs)
        return context


#@login_required
def MarcarEntrada(request):

    if request.POST :
        form = MarcarEntradaForm(request.POST, request.FILES)
        if form.is_valid():
            campo_anexo = form.cleaned_data['anexo_usuario']
            actividad = Actividad.objects.get (id = request.POST['id_actividad'])
            entrada = Entrada(
                fecha_ingreso = timezone.now(),
                usuario = request.user,
                actividad = actividad,
                anexo_usuario=campo_anexo
            )
            entrada.save()    
            return redirect('/actividad/')
    else:
        form = MarcarEntradaForm
        #actividades = Actividad.Objects.get(inscritos = request.user,
        actividad= Actividad.objects.filter(
            Q(inscritos = request.user)
        )
        
        for a in actividad:
            try:
                entrada = Entrada.objects.get(
                    actividad = a,
                    usuario = request.user
                )
                print u'Existe'
                pass
            except:
                print u'NO EXISTE'
                return render(request, 'actividad/marcar_entrada.html', {
                    'actividad': a,
                    'fecha_hora': timezone.now(),
                    'actividades_pendientes': True,
                    'form': form
                })



        return render(request, 'actividad/marcar_entrada.html', {
            'actividades_pendientes': False,
        })





class ActividadDeleteView(DeleteView):
    model = Actividad
    success_url = reverse_lazy('actividad')
    template_name="actividad/actividad_confirm_delete.html"
    
    def delete(self, request, *args, **kwargs):
        comunicacion = Group.objects.get(name="Comunicación Social").user_set.all()
        self.object = self.get_object()
        actividad = Actividad.objects.get(id=self.get_object().pk)
        
        if self.request.user in comunicacion and actividad.fecha_salida > timezone.now():
            #self.object = self.get_object()
            success_url = self.get_success_url()
            
            
            if os.path.isfile(self.object.anexo_actividad.path):
                
                os.remove(self.object.anexo_actividad.path)
            
            self.object.delete()
            
            return HttpResponseRedirect(success_url)
        else:
            raise Http404()

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        actividad = Actividad.objects.get(id=self.get_object().pk)
        comunicacion = Group.objects.get(name="Comunicación Social").user_set.all()
        context = self.get_context_data(object=self.object)
        if self.request.user in comunicacion and actividad.fecha_salida > timezone.now():
            context = self.get_context_data(object=self.object)
            return self.render_to_response(context)
        else:
            raise Http404()
        
    


"""
Total Grupos de usuarios:
Comunicaci?n Social
Direcci?n Ejecutiva
Direcci?n de Gesti?n
Presidencia
Talento Humano
Trabajador

El usuario admin se encuentra en todos los grupos de usuario
"""

