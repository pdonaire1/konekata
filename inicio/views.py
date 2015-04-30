# -*- coding: utf-8 -*-
from django.shortcuts import render, render_to_response, RequestContext, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.contrib import auth
#----------------------------------------------------------------------------------------------
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
from django.utils import timezone
from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse
import datetime
from django.core.mail import send_mail, BadHeaderError
from django.forms import ModelForm
from django import forms
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.decorators import login_required, user_passes_test
#from .models import Usuario
import csv
from proyectos.models import EquipoTrabajo, Proyecto
from .forms import RecuperarPassForm, CambiarPasswordForm
from django.core.mail import EmailMessage, send_mass_mail
from django.conf import settings
from konekata.settings import DEFAULT_FROM_EMAIL


def SubirCSV(request):
    csv_filepathname="/home/c30/desarrollos/grupos.csv"
    dataReader = csv.reader(open(csv_filepathname), delimiter=';', quotechar='"')
    cont = 0
    grupo1 = Group.objects.get(name="Trabajador")
    for row in dataReader:
        #if row[0] != 'ZIPCODE': # ignoramos la primera línea del archivo CSV
        
        try:
            user = User()
            user.username = row[2]
            user.name = row[1]
            user.set_password(123)
            
            user.save()
            if (row[3] == 'Gestión Interna'):
                grupo2 = Group.objects.get(name="Dirección de Gestión")
                user.groups.add(grupo2)
            if (row[3] == 'Presidente'):
                grupo2 = Group.objects.get(name="Presidencia")
                user.groups.add(grupo2)
            if (row[3] == 'Directora Ejecutiva'):
                grupo2 = Group.objects.get(name="Dirección Ejecutiva")
                user.groups.add(grupo2)
            user.groups.add(grupo1)    
        except:
            pass
        
        print cont
        print user.name
        cont += 1
    return HttpResponse("Ya están cargados")

def SubirEquipoCSV(request):
    csv_filepathname="/home/c30/desarrollos/equipos.csv"
    dataReader = csv.reader(open(csv_filepathname), delimiter=';', quotechar='"')
    
    proyecto = Proyecto()
    proyecto.nombre = "Proyecto1"
    proyecto.descripcion = "Prueba del Proyecto1"

    for row in dataReader:
        
        if row[0] != 'Proyecto': # ignoramos la primera línea del archivo CSV
            equipo = EquipoTrabajo()
            equipo.nombre = row[0]
            row[2] = row[2].upper()
            cv = User.objects.get(first_name = row[2])
            equipo.cara_visible = cv
            row[1] = row[1].upper()
            dp = User.objects.get(first_name = row[1])
            equipo.director_proyecto = dp
            lista = row[3].split('-')
            print lista
            for i in lista:
                equipo.integrante.add(i)
            
            
    return HttpResponse("Ya están cargados")

class UsuarioUpdateView(UpdateView):
    model = User
    success_url = reverse_lazy('konekata')
    
    def get_form_class(self):
        return model_forms.modelform_factory(
            self.model,
            exclude=[
                'is_staff',
                'is_active',
                'is_superuser',
                'groups',
                'user_permissions',
                'date_joined',
                'password',
                'last_login',
            ]
        )
    def form_valid(self, form):
        if form.is_valid():
            #super(UsuarioUpdateView, self).form_valid(form)
            #return redirect('/konekata/')
            return super(UsuarioUpdateView, self).form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))
    
    def get_form(self, form_class):
        form = super(UsuarioUpdateView, self).get_form(form_class)
        return form
    
    def get_context_data(self, **kwargs):
        if self.request.user.pk == self.object.pk:
            context = super(UsuarioUpdateView, self).get_context_data(**kwargs)
            return context
        else:
            return Http404
        

@login_required
def app_home(request):
    template = "home.html"
    return render_to_response(template, context_instance=RequestContext(request))
 
@login_required
def konekata(request):
    #presidencia = Group.objects.get(name="Presidencia").user_set.all()
    #direccion_ejecutiva = Group.objects.get(name="Dirección Ejecutiva").user_set.all()
    #talento = Group.objects.get(name="Talento Humano").user_set.all()
    trabajador = Group.objects.get(name="Trabajador").user_set.all()
    
    #bandera_direccion   = False
    bandera_trabajador  = False
    #bandera_presidencia = False
    #bandera_talento     = False
    
    #if request.user in presidencia:
    #    bandera_presidencia  = True
    #if request.user in direccion_ejecutiva:
    #    bandera_direccion = True
    #if request.user in talento:
    #    bandera_talento  = True
    if request.user in trabajador:
        bandera_trabajador  = True
    
    
    
    if request.user in trabajador:
        return render(
            request,
            'konekata.html',
            {
                'Trabajador': bandera_trabajador
            }
        )
    return Http404
    #return HttpResponseRedirect('/abrir/')
def permiso(request):
    presidencia = Group.objects.get(name="Presidencia").user_set.all()
    direccion_ejecutiva = Group.objects.get(name="Dirección Ejecutiva").user_set.all()
    talento = Group.objects.get(name="Talento Humano").user_set.all()
    trabajador = Group.objects.get(name="Trabajador").user_set.all()
    gestion = Group.objects.get(name="Dirección de Gestión").user_set.all()
    
    bandera_direccion   = False
    bandera_trabajador  = False
    bandera_presidencia = False
    bandera_talento     = False
    bandera_gestion     = False
    
    if request.user in presidencia:
        bandera_presidencia  = True
    if request.user in direccion_ejecutiva:
        bandera_direccion = True
    if request.user in talento:
        bandera_talento  = True
    if request.user in trabajador:
        bandera_trabajador  = True
    if request.user in gestion:
        bandera_gestion = True
    
    
    
    if request.user in trabajador:
        return render(
            request,
            'permiso.html',
            {
                'Presidencia': bandera_presidencia,
                'Direccion': bandera_direccion,
                'Talento': bandera_talento,
                'Trabajador': bandera_trabajador,
                'Gestion': bandera_gestion
            }
        )
    
    return HttpResponseRedirect('/abrir/')

def proyecto(request):
    presidencia = Group.objects.get(name="Presidencia").user_set.all()
    direccion_ejecutiva = Group.objects.get(name="Dirección Ejecutiva").user_set.all()
    talento = Group.objects.get(name="Talento Humano").user_set.all()
    trabajador = Group.objects.get(name="Trabajador").user_set.all()
    
    bandera_direccion   = False
    bandera_trabajador  = False
    bandera_presidencia = False
    bandera_talento     = False
    
    if request.user in presidencia:
        bandera_presidencia  = True
    if request.user in direccion_ejecutiva:
        bandera_direccion = True
    if request.user in talento:
        bandera_talento  = True
    if request.user in trabajador:
        bandera_trabajador  = True
    
    
    
    if request.user in trabajador:
        return render(
            request,
            'proyecto.html',
            {
                'Presidencia': bandera_presidencia,
                'Direccion': bandera_direccion,
                'Talento': bandera_talento,
                'Trabajador': bandera_trabajador
            }
        )
    
    return HttpResponseRedirect('/abrir/')

def inicio(request):
    form = AuthenticationForm()
    user = request.user
    if user:
        if user.is_active and user.is_superuser:
            return HttpResponseRedirect('/admin/')
    
    return redirect('/abrir/')
    return render_to_response(
        'inicio.html',
        RequestContext(
            request, {'form':form}
        )
    )

def actividad(request):
    trabajador = Group.objects.get(name="Trabajador").user_set.all()
    comunicacion = Group.objects.get(name="Comunicación Social").user_set.all()
    if request.user in comunicacion:
        return render(
            request,
            'actividad.html',
            {
                'Trabajador': True,
                'Comunicacion': True
            }
        )
    if request.user in trabajador:
        return render(
            request,
            'actividad.html',
            {
                'Trabajador': True
            }
        )
    return Http404

def manual(request):
    trabajador = Group.objects.get(name="Trabajador").user_set.all()
    presidencia = Group.objects.get(name="Presidencia").user_set.all()
    
    return render(
        request,
        'manual.html',
        {
            'Trabajador': True
        }
    )
    
def app_login(request):
    form = AthenticationForm()
    ctx = {"form":form, "mensaje":""}
    if request.method == "POST":
        form = AthenticationForm(request.POST)
        if form.is_valid():
            usuario = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=usuario, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect('/')
                else:
                    ctx = {"form":form, "mensaje": "Usuario Inactivo"}
                    return render_to_response("login.html",ctx, context_instance=RequestContext(request))
            else:
                ctx = {"form":form, "mensaje": "Datos incorrecto"}
                return render_to_response("login.html",ctx, context_instance=RequestContext(request))	
    return render_to_response("login.html",ctx, context_instance=RequestContext(request))
 
def app_logout(request):
    logout(request)
    return HttpResponseRedirect('/')


# ___________________________________________________________________________________________________

def login(request):
    username = request.POST['username']
    password = request.POST['password']
    user = auth.authenticate(username=username, password=password)
    if user is not None and user.is_active:
        # Correct password, and the user is marked "active"
        auth.login(request, user)
        # Redirect to a success page.
        return HttpResponseRedirect("/account/loggedin/")
    else:
        # Show an error page
        return HttpResponseRedirect("/account/invalid/")




def logout(request):
    auth.logout(request)
    # Redirect to a success page.
    return HttpResponseRedirect("/account/loggedout/")



def recuperar_password(request):
    if request.POST:
        form = RecuperarPassForm(request.POST)
        if form.is_valid():
            correo = form.cleaned_data.get('correo')
            usuario = User.objects.get(email=correo)
            
            asunto = "Recuperación de contraseña"
            mensaje = ("Su usuario es: " + str(usuario.username) + " y su contraseña: " +
                str(usuario.password) + ". Le recomendamos cambiar su contraseña"
            )
            
            send_mail(
                asunto, mensaje, DEFAULT_FROM_EMAIL,
                [usuario.email], fail_silently=False
            )
            formulario = RecuperarPassForm()
            
            return render(request, 'recuperar_password.html',{
                'form': formulario,
                'correo_enviado': True
            })
            try:
              
                pass
            except:
                print u'******-'
                formulario = RecuperarPassForm()
                return render(request, 'recuperar_password.html',{
                    'form': formulario,
                    'usuario_no_existe': True
                })
        else:
            return render(request, 'recuperar_password.html',{
                'form': form
            })
    else:
        form = RecuperarPassForm()
        return render(request, 'recuperar_password.html',{
            'form': form
        })


def cambiar_password(request, pk):
    
    if request.POST:
        form = CambiarPasswordForm(request.POST)
        if form.is_valid():
            username=request.user.username
            password=form.cleaned_data['password']
            usuario = authenticate(username=username, password=password)
            print usuario
            if usuario is not None:
                if form.cleaned_data['password_dos'] == form.cleaned_data['password_uno']:
                    usuario.set_password(form.cleaned_data['password_uno'])
                    usuario.save()
            else:
                return render(request, 'cambiar_password.html',{
                    'form': form,
                    'pk': pk,
                    'error':True
                })

            return render(request, 'cambiar_password.html',{
                'pk': pk,
                'correcto':True
            })
        else:
            return render(request, 'recuperar_password.html',{
                'form': form
            })
    else:
        
        form = CambiarPasswordForm()
        return render(request, 'cambiar_password.html',{
            'form': form,
            'pk': pk
        })


#######################################################3


