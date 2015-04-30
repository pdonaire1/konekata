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
    DeleteView, TemplateView
)
from .models import Permiso
from .models import Observaciones
from .filters import PermisoFilterSet
from .filters import PermisoLeidasFilterSet
from .filters import PermisoSinLeerFilterSet
from .filters import Permisos_usuarioFilterSet
from .filters import Permisos_ausentesFilterSet
from .filters import Permisos_suplenteFilterSet


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
from django.contrib.formtools.wizard.views import SessionWizardView
from forms import PermisoCrearForm1, PermisoCrearForm2
from django.contrib.formtools.wizard.forms import ManagementForm
from django.contrib.formtools.wizard.views import SessionWizardView
from django.utils.datastructures import SortedDict
from django.utils import six
import copy
from django.core.exceptions import ValidationError
from django.template.response import TemplateResponse
from proyectos.models import EquipoTrabajo
from django.core import serializers
from forms import ObservacionesForm
from django.forms.formsets import formset_factory
from django.forms.models import inlineformset_factory
from django.core.urlresolvers import resolve
from django.core import mail
import json

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.mail import EmailMessage, send_mass_mail
#from django.core.mail import EmailMultiAlternatives # Enviamos HTML
#c30@debian:~/desarrollos/asambleas$ less settings.py.orig
#c30@debian:~/desarrollos/asambleas$ python -m smtpd -n -c DebuggingServer localhost:1025
from django.contrib.formtools.wizard.storage.exceptions import NoFileStorageConfigured
from django.contrib.formtools.wizard.storage import get_storage
from django.contrib.formtools.wizard.forms import ManagementForm
import os
from konekata.settings import DEFAULT_FROM_EMAIL


class PermisoCrearWizard(SessionWizardView):
    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'anexos_permiso'))
    #anexo = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'anexos'))
    
    def show_message_form_condition(wizard):
        cleaned_data = wizard.get_cleaned_data_for_step('0') or {}
        return cleaned_data.get('leave_message', True)

    def get_form_list(self):

        form_list = SortedDict()
        for form_key, form_class in six.iteritems(self.form_list):
            condition = self.condition_dict.get(form_key, True)
            if callable(condition):
                condition = condition(self)
            if condition:
                form_list[form_key] = form_class
        return form_list

    def done(self, form_list, **kwargs):
        if form_list:
            fo1 = form_list[0].cleaned_data
            fo2 = form_list[1].cleaned_data

            permiso = Permiso(
                solicitante= self.request.user,#fo2['solicitante'],
                fecha_solicitud = timezone.now(),#fo2['fecha_solicitud'],
                inicio = fo1['inicio'],
                fin = fo1['fin'],
                observacion = fo2['observacion'],
                suplente = fo2['suplente'],
                aprobado = False,
                enviado = False,
                revisado = False,

                #equipo_trabajo = fo2['equipo_trabajo'],
                aprobado_cv = None,
                aprobado_dp = None,
                aprobado_suplente = None,
                enviado_para = 'Suplente',
                anexo_permiso = fo2['anexo_permiso']
            )
            # SI YO SOY EL CARA VISIBLE O EL DIRECTOR DEL PROYECTO ENTNCES APRUEBALO DE UNA VEZ
            equipos = EquipoTrabajo.objects.filter(
                Q(cara_visible = self.request.user)
                |Q(director_proyecto = self.request.user)
            )
            for i in equipos:
                print i
                if (self.request.user == i.cara_visible):
                    permiso.aprobado_cv = True
                    permiso.aprobado_cv_por = self.request.user
                if self.request.user == i.director_proyecto:
                    permiso.aprobado_dp = True
                    permiso.aprobado_dp_por = self.request.user
                if permiso.aprobado_cv == True and permiso.aprobado_dp == True:
                        break

            if permiso.suplente == None:
                permiso.aprobado_suplente = True
            if permiso.aprobado_cv == True and permiso.aprobado_dp == True and permiso.suplente == True:
                permiso.enviado_para = "Talento"

            permiso.save()


        else:
            html = '<p>El formulario no es válido</p>'
            return HttpResponse(html);
        return HttpResponseRedirect('/permiso/editar/%s'%permiso.id)


    def render_revalidation_failure(self, step, form, **kwargs):
        self.storage.current_step = step
        #print self.storage.current_step
        return self.render(form, **kwargs)

    def post(self, *args, **kwargs):
        wizard_goto_step = self.request.POST.get('wizard_goto_step', None)
        if wizard_goto_step and wizard_goto_step in self.get_form_list():
            return self.render_goto_step(wizard_goto_step)

        # Check if form was refreshed
        management_form = ManagementForm(self.request.POST, prefix=self.prefix)
        if not management_form.is_valid():
            raise ValidationError(
                _('ManagementForm data is missing or has been tampered.'),
                code='missing_management_form',
            )

        form_current_step = management_form.cleaned_data['current_step']
        if (form_current_step != self.steps.current and
                self.storage.current_step is not None):
            self.storage.current_step = form_current_step

        form = self.get_form(data=self.request.POST, files=self.request.FILES)

        if form.is_valid():
            if self.steps.current=='0':
                context = super(PermisoCrearWizard, self).get_context_data(form=form, **kwargs)
                i = context['form'].cleaned_data
                f_inicio = i['inicio']
                f_fin = i['fin']

                if f_inicio > f_fin:
                    html = '<p>Error la fecha de inicio es mayor que la fecha fin</p>'
                    #return HttpResponse(html)
                    return render(
                        self.request,
                        'formtools/wizard/wizard_form.html',
                        {
                            'inicio_mayor': True,
                            'wizard': context
                        }
                    )
                elif f_inicio == f_fin:
                    html = '<p>Error la fecha de inicio es exactamete igual que la fecha fin</p>'
                    return HttpResponse(html)
                elif f_inicio.weekday() == 5 or f_inicio.weekday() == 6:
                    html = '<p>Error la fecha de inicio es un dia no laborable</p>'
                    return HttpResponse(html)
                elif f_fin.weekday() == 5 or f_fin.weekday() == 6:
                    html = '<p>Error la fecha de culminación es un dia no laborable</p>'
                    return HttpResponse(html)


            if self.steps.current=='1':

                context = super(PermisoCrearWizard, self).get_context_data(form=form, **kwargs)
                context.update({'solicitante': self.request.user })


            # if the form is valid, store the cleaned data and files.
            self.storage.set_step_data(self.steps.current, self.process_step(form))
            self.storage.set_step_files(self.steps.current, self.process_step_files(form))
            if self.steps.current == self.steps.last:
                # no more steps, render done view
                return self.render_done(form, **kwargs)
            else:
                # proceed to the next step
                return self.render_next_step(form)

        return self.render(form)



    def get_form(self, step=None, data=None, files=None):
        form = super(PermisoCrearWizard, self).get_form(step, data, files)

        if step is None:
            step = self.steps.current




        if step == '1':
            try:
                datos=self.request.POST

                form.user = self.request.user
                context = super(PermisoCrearWizard, self).get_context_data(form=form)
                context2 = copy.copy(context)
                i = context2['form']#.cleaned_data

                inicio = datos['0-inicio']
                fin = datos['0-fin']


                now = timezone.now()

                #5 sabado, 6 domingo

                permisos1 = Permiso.objects.filter(
                    Q(aprobado=True)

                )& Permiso.objects.filter(
                    Q(inicio__range = (inicio, fin))
                    |Q(fin__range = (inicio, fin))
                )

                permisos2 = Permiso.objects.filter(
                    Q(revisado=False),
                    Q(enviado=True)
                )& Permiso.objects.filter(
                    Q(inicio__range = (inicio, fin))
                    |Q(fin__range = (inicio, fin))
                )

                context['form'].fields['suplente'].queryset = User.objects.exclude(
                    Q(solicitante__in=list(permisos1))|
                    Q(suplente__in=list(permisos1))
                    #Hay que colocarle | porque me toma los suplentes que esten tanto en solicitante
                    #como en suplente si coloco and y por esto no agarra algunos usuarios que estan
                    #en suplente y que no estan en usuarios, y viceversa
                )& User.objects.exclude(
                    Q(solicitante__in=list(permisos2))|
                    Q(suplente__in=list(permisos2)),
                )& User.objects.exclude(
                    Q(username = self.request.user)
                )
            except:
                pass



        return form

    def get_context_data(self, form, **kwargs):
        context = super(PermisoCrearWizard, self).get_context_data(form=form, **kwargs)
        if self.steps.current == '1':
            #print u'x'
            context.update({'another_var': True})
        return context


#
#class ExcluirCampos(forms.ModelForm):
#    class Meta:
#        model = Permiso
#        exclude = (
#            'aprobado',
#            'revisado',
#            'solicitante',
#            #'aprobacion_a',
#            #'aprobacion_b',
#            #'aprobado_por',
#        )

#def PermisoCreate1(request):
#    users_in_group = Group.objects.get(name="Trabajador").user_set.all()
#    if request.user in users_in_group:# or request.user in users_in_group2 :
#        f_inicio= request.POST.get('f_inicio')
#        f_fin= request.POST.get('f_fin')
#        if request.POST:
#            if not f_inicio:
#                raise ValueError('ERROR llene todos los campos')
#            if not f_fin:
#                raise ValueError('ERROR llene todos los campos')
#            else:
#                response = TemplateResponse(request, 'permiso_form.html', {'f_inicio': f_inicio, 'f_fin': f_fin})
#                return HttpResponseRedirect('/permiso/crear')
#        else:
#            return render(request, 'permisos/permiso_create1.html', {'bandera': False})
#    raise Http404()

#@login_required
#@user_passes_test(lambda u: u.groups.filter(name='Trabajador').count() == 0, login_url='/myapp/negado/')
class PermisoCreateView(CreateView):
    model = Permiso
    success_url = reverse_lazy('listar-por-usuarios')

    def get_form_class(self):
        return model_forms.modelform_factory(
            self.model,
            exclude=[
                'aprobado',
                'revisado',
                'solicitante',
                #'enviado',
                'aprobacion_a',
                'aprobacion_b',
                'aprobado_por',
                #'fecha_creacion',
                'fecha_solicitud',
                'enviado',
            ]
        )

    def form_valid(self, form):
        if form.is_valid():
            form.instance.aprobado = False
            form.instance.solicitante = self.request.user
            form.instance.revisado = False
            form.instance.aprobacion_a = False
            form.instance.aprobacion_b = False
            form.instance.fecha_solicitud = timezone.now()
            form.instance.enviado = False


            super(PermisoCreateView, self).form_valid(form)
            return redirect('/permiso/editar/%s'%self.object.pk)
        else:
            return self.render_to_response(self.get_context_data(form=form))


    def get_form(self, form_class):
        form = super(PermisoCreateView, self).get_form(form_class)
        form.fields['inicio'].widget.attrs.update({'class': 'datepicker'})
        return form

    def get_context_data(self, **kwargs):

        users_in_group = Group.objects.get(name="Trabajador").user_set.all()
        if self.request.user in users_in_group:

            if self.request.POST:
                inicio = request.POST.get('f_inicio')
                fin = request.POST.get('f_fin')
            context = super(PermisoCreateView, self).get_context_data(**kwargs)
            now = timezone.now()
            permisos = Permiso.objects.filter(
                solicitante=self.request.user,
                aprobado=True,
            )| Permiso.objects.filter(
                Q(inicio__range = (inicio, fin))
                | Q(fin__range = (inicio, fin)),#.order_by('solicitante')
            )
            lista = []
            for obj in permisos:
                lista.append(obj.solicitante)
                lista.append(obj.suplente)
                print obj.solicitante
                print obj.suplente
            #print lista
            print "-----------------------------------------------------"
            context['form'].fields['suplente'].queryset = User.objects.exclude(
                Q(solicitante__in=list(permisos))|
                Q(suplente__in=list(permisos))
            )& User.objects.exclude(
                Q(username = self.request.user)
            )

            return context



class PermisoUpdateView(UpdateView):

    model = Permiso
    template_name = 'permisos/editar_update_form.html'
    success_url = reverse_lazy('permiso')



    def __unicode__(self, pk, *arg, **kwargs):
        pass

    def get_form_class(self):
        return model_forms.modelform_factory(
            self.model,
            exclude=[
                'aprobado',
                'revisado',
                'solicitante',
                'aprobado_por',
                'aprobacion_a',
                'aprobacion_b',
                'fecha_solicitud',
                'aprobado_cv',
                'aprobado_dp',
                'aprobado_suplente',
                'enviado_para',
                'aprobado_dp_dos',
                'aprobado_dp_por',
                'aprobado_cv_por',
                'aprobado_dp_dos_por',
            ]
        )

    def form_valid(self, form):

        if form.is_valid():
            obj = Permiso.objects.get(id = self.object.pk)
            if obj.revisado and obj.aprobado != None and obj.enviado:
                raise Http404()



            else:

                if obj.solicitante == self.request.user:
                    formulario = form.save(commit = False)

                    inicio = form.cleaned_data['inicio']
                    fin = form.cleaned_data['fin']
                    suplente = form.cleaned_data['suplente']

                    if inicio > fin:
                        raise ValidationError(' La fecha de inicio es mayor que la fecha fin del permiso.')
                    if inicio == fin:
                        raise ValidationError(' La fecha y hora de inicio igual que la fecha fin del permiso.')
                    if inicio.weekday() == 5 or inicio.weekday() == 6:
                        html = "<html><p>La Fecha de inicio no es un día laborable.</p></html>"
                        return HttpResponse(html)
                    if fin.weekday() == 5 or fin.weekday() == 6:
                        html = "<html><p>La Fecha de fin no es un día laborable.</p></html>"
                        return HttpResponse(html)


                    permisos1 = Permiso.objects.filter(
                        Q(aprobado=True)
                    )& Permiso.objects.filter(
                        Q(inicio__range = (inicio, fin))
                        |Q(fin__range = (inicio, fin))
                    )
                    permisos2 = Permiso.objects.filter(
                        Q(revisado=False),
                        Q(enviado=True)
                    )& Permiso.objects.filter(
                        Q(inicio__range = (inicio, fin))
                        |Q(fin__range = (inicio, fin))
                    )
                    lista=[]
                    for i in permisos1:
                        lista.append(i.solicitante)
                        lista.append(i.suplente)
                    for i in permisos2:
                        lista.append(i.solicitante)
                        lista.append(i.suplente)

                    if suplente in lista and suplente != None:
                        

                        #los suplentes disponibles:::
                        u = User.objects.exclude(
                                Q(solicitante__in=list(permisos1))|
                                Q(suplente__in=list(permisos1))
                            )& User.objects.exclude(
                                Q(solicitante__in=list(permisos2))|
                                Q(suplente__in=list(permisos2))
                            )& User.objects.exclude(
                                Q(username = self.request.user)
                            )
                        html ="<html><p>Error: El suplente no está disponible</p><br><br><u>Suplentes Disponibles para el nuevo rango de fechas:</u><br>"
                        for i in u:
                            html = html + '<br>- ' + str(i.username)
                        html = html + '</html>'
                        context = self.get_context_data(form=form)
                        context['sup_no_disponible'] = True
                        return self.render_to_response(context)

                    # esto es al momento de enviar o guardar
                    formulario.aprobado = False
                    formulario.revisado = False
                    formulario.save()

                    equipos = EquipoTrabajo.objects.filter(
                        integrante = self.request.user
                        #Q(cara_visible = self.request.user)|
                        #Q(director_proyecto = self.request.user)
                    )#.values_list('cara_visible.email', 'director_proyecto.email')


                    asunto = "Solicitud de Permiso"
                    mensaje1 = (
                        "Se ha enviado una solicitud de permiso con su persona como suplente del solicitante: " + str(self.request.user)
                        + ". \nPara mas información entrar a konekata."
                    )
                    mensaje = (
                        "Se ha enviado un nuevo permiso para su correccion, por parte de " + str(self.request.user)
                        + ". \nPara mas información entrar a Konekata."
                    )
                    mensaje2 = "Usted ha enviado la solicitud de un nuevo permiso con éxito, para mayor información revisar el estatus en konekata."
                    #para el solicitante
                    try:
                        send_mail(
                            asunto, mensaje2, DEFAULT_FROM_EMAIL,
                            [self.request.user.email], fail_silently=False
                        )
                        #para suplente
                        send_mail(
                            asunto, mensaje1, DEFAULT_FROM_EMAIL,
                            [obj.suplente.email], fail_silently=False
                        )
                    except:
                        pass
                    emails = []

                    for i in equipos:
                        if not (str(i.cara_visible.email) in emails):
                            emails.append(str(i.cara_visible.email))
                        if not (str(i.director_proyecto.email) in emails):
                            emails.append(str(i.director_proyecto.email))
                    try:
                        send_mail(
                            asunto, mensaje, DEFAULT_FROM_EMAIL,
                            emails, fail_silently=False
                        )
                    except:
                        pass

                    return super(PermisoUpdateView, self).form_valid(form)
                else:
                    raise Http404()
        else:

            return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        codigo = self.object.pk
        permiso = Permiso.objects.get(pk = codigo)
        if permiso.enviado:
            #html = "<html><body><center>El Permiso no se puede modificar porque ya está enviado.</center></body></html>"
            return #HttpResponse(html)
        elif permiso.solicitante != self.request.user:
            #html = "<html><body><center>Error el permiso no corresponde al usuario logeado.</center></body></html>"
            return #HttpResponse(html)
        else:
            pass

        """
                ******Combinacion para Marcar para correccion supl,cv,dp ******
                    apreobado=, revisado =, enviado = ,

                ******Combinacion para negar por supl,cv,dp  ******
                    apreobado=, revisado =, enviado = ,

                ******Combinacion para aprobar por supl,cv,dp  ******
                    apreobado=, revisado =, enviado = ,

                ******Combinacion para Marcar para correccion TH ******
                    apreobado=none, revisado =true, enviado = false,

                ******Combinacion para Aprobado por TH ******
                    apreobado=true, revisado =true, enviado = true,

                ******Combinacion para Marcar para negador por TH ******
                    aprobado = False, revisado = True, enviado=true


        """
        if permiso.revisado and permiso.aprobado != None and enviado:
            # REBOTA
            return render_to_response('permisos/editar_update_form.html', { 'form': False})
        else:
            #PUEDE MODIFICAR
            context = super(PermisoUpdateView, self).get_context_data(**kwargs)

            permiso = Permiso.objects.get(id = self.object.pk)
            inicio = permiso.inicio
            fin = permiso.fin
            permisos1 = Permiso.objects.filter(
                    Q(aprobado=True)
                )& Permiso.objects.filter(
                    Q(inicio__range = (inicio, fin))
                    |Q(fin__range = (inicio, fin))
                )

            permisos2 = Permiso.objects.filter(
                    Q(revisado=False),
                    Q(enviado=True)
                )& Permiso.objects.filter(
                    Q(inicio__range = (inicio, fin))
                    |Q(fin__range = (inicio, fin))
                )

            context['form'].fields['suplente'].queryset = User.objects.exclude(
                Q(solicitante__in=list(permisos1))|
                Q(suplente__in=list(permisos1))
            )& User.objects.exclude(
                Q(solicitante__in=list(permisos2))|
                Q(suplente__in=list(permisos2))
            )& User.objects.exclude(
                Q(username = self.request.user)
            )
            context['permisos']= Permiso.objects.all()
            permisos = Permiso.objects.all()
            context['usuarios'] = User.objects.all()
            usuarios = User.objects.all()
            usuarios = User.objects.all()

            return context

    def get_success_url(self):
        return reverse('permiso')


class PermisoDeleteView(DeleteView):
    model = Permiso
    success_url = reverse_lazy('permiso')
    #success_message = "eliminado exitosamente"
    #success_url = reverse_lazy('permiso-listar')
    #    return reverse('permiso-list')


    def delete(self, request, *args, **kwargs):
        """
        Calls the delete() method on the fetched object and then
        redirects to the success URL.
        """
        #presidencia = Group.objects.get(name="Presidencia").user_set.all()
        self.object = self.get_object()
        permiso = Permiso.objects.get(id=self.get_object().pk)
        if self.request.user != permiso.solicitante:
            raise Http404()
        if (
            permiso.enviado
            and permiso.revisado != True
        ):
            context = self.get_context_data(object=self.object)
            context['enviado'] = True
            return self.render_to_response(context)
        if self.request.user == permiso.solicitante:
            #self.object = self.get_object()
            success_url = self.get_success_url()
            if os.path.isfile(self.object.anexo_permiso.path):
                os.remove(self.object.anexo_permiso.path)
            self.object.delete()

            return HttpResponseRedirect(success_url)
        else:
            raise Http404()

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        permiso = Permiso.objects.get(id=self.get_object().pk)

        if self.request.user != permiso.solicitante:
            raise Http404()

        context = self.get_context_data(object=self.object)
        if (
            permiso.enviado
            and permiso.revisado != True
        ):
            context['enviado'] = True
            return self.render_to_response(context)
        else:
            context = self.get_context_data(object=self.object)
            return self.render_to_response(context)


    def form_valid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """
        if request.is_valid():
            return HttpResponseRedirect(self.get_success_url())
        else:
            raise Http404()

    pass

class PermisoDetailView(DetailView):

    model = Permiso

    def get_context_data(self, **kwargs):
        context = super(PermisoDetailView, self).get_context_data(**kwargs)
        #context['now'] = timezone.now()
        return context

    pass

#este es para listar solo los permisos enviados a talento humano para presidencia y los otros
#existe otra clase mas abajo
class PermisoListView(ListView):
    model = Permiso
    template_name = 'permiso_list.html'
    paginate_by = 7
    #paginate_by = 20

    def get(self, request, *args, **kwargs):
        super(PermisoListView, self).get(request, *args, **kwargs)

        talento = Group.objects.get(name="Talento Humano").user_set.all()
        object_list = []
        if request.user in talento:
            queryset = Permiso.objects.filter(
                Q(enviado_para='Talento'),
                Q(enviado=True),
                Q(aprobado_suplente=True),
                Q(aprobado_cv = True),
                Q(aprobado_dp = True),
            )|Permiso.objects.filter(
                Q(enviado = True),
                Q(revisado=True),
                Q(aprobado = True)
                |Q(aprobado=False)
            ).order_by('inicio')
            filterset = PermisoFilterSet(self.request.GET or None, queryset=queryset)
            for obj in filterset:
                object_list.append(obj)

        else:
            raise Http404()

        context = self.get_context_data(object_list=object_list)

        if request.user in talento:
            context['talento'] = True

        context['url_destino'] = 'procesar-talento/'

        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(PermisoListView, self).get_context_data(**kwargs)
        trabajador = Group.objects.get(name="Trabajador").user_set.all()
        if self.request.user in trabajador:
            context['filterset'] = Permisos_usuarioFilterSet(self.request.GET or None)
        talento = Group.objects.get(name="Talento Humano").user_set.all()
        if self.request.user in talento:
            context['filterset'] = PermisoFilterSet(self.request.GET or None)

        return context


class PermisosDeUsuarioListView(ListView):
    model = Permiso
    paginate_by = 7

    def get(self, request, *args, **kwargs):
        super(PermisosDeUsuarioListView, self).get(request, *args, **kwargs)
        queryset = Permiso.objects.filter(solicitante = self.request.user).order_by('inicio')
        filterset = Permisos_usuarioFilterSet(self.request.GET or None, queryset=queryset)
        object_list = []
        for obj in filterset:
            object_list.append(obj)
        context = self.get_context_data(object_list=object_list)
        context['trabajador']= True
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(PermisosDeUsuarioListView, self).get_context_data(**kwargs)
        context['filterset'] = Permisos_usuarioFilterSet(self.request.GET or None)


        return context
class PermisoPresidenciaListView(ListView):
    model = Permiso
    paginate_by = 7

    def get(self, request, *args, **kwargs):
        super(PermisoPresidenciaListView, self).get(request, *args, **kwargs)
        presidencia = Group.objects.get(name="Presidencia").user_set.all()
        object_list = []

        if request.user in presidencia:
            queryset = Permiso.objects.filter(
                enviado=True,
                enviado_para='Presidencia',
            )|Permiso.objects.filter(
                Q(enviado = True),
                Q(revisado=True),
                Q(aprobado = True)
                |Q(aprobado=False)
            ).order_by('inicio')

            filterset = PermisoFilterSet(self.request.GET or None, queryset=queryset)
            for obj in filterset:
                object_list.append(obj)

        else:
             raise Http404()
        context = self.get_context_data(object_list=object_list)
        if request.user in presidencia:
            context['presidencia']= True
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(PermisoPresidenciaListView, self).get_context_data(**kwargs)
        context['filterset'] = PermisoFilterSet(self.request.GET or None)
        context['url_destino'] = 'procesar-presidencia/'
        return context

class PermisoDireccionEjecutivaListView(ListView):
    model = Permiso
    paginate_by = 7
    #template_name = 'permiso/permiso_direccion_list.html'

    def get(self, request, *args, **kwargs):
        super(PermisoDireccionEjecutivaListView, self).get(request, *args, **kwargs)
        direccion = Group.objects.get(name="Dirección Ejecutiva").user_set.all()
        presidencia = Group.objects.get(name="Presidencia").user_set.all()
        object_list = []

        if request.user in direccion:

            todos_p = Permiso.objects.all()
            ahora = timezone.now()
            ahora.astimezone(timezone.utc).replace(tzinfo=None)

            # ******ACTUALIZO LOS PERMISOS ********
            presidente_ausente = False
            for p in todos_p:
                if p.solicitante in presidencia or p.suplente in presidencia:
                    if p.inicio < ahora and p.fin > ahora:
                        presidente_ausente = True
            if presidente_ausente == True:
                for p in todos_p:
                    if p.enviado_para == 'Presidencia':
                        p.enviado_para = 'Direccion'
            # ****** NO BORRAR ********
            # ******ACTUALIZO LOS PERMISOS ********
            #cambio los permisos a direccion ejecutiva si el presidente no se encuentra


            queryset = Permiso.objects.filter(
                enviado=True,
                enviado_para='Direccion',
            )|Permiso.objects.filter(
                Q(enviado = True),
                Q(revisado=True),
                Q(aprobado = True)
                |Q(aprobado=False)
            ).order_by('inicio')

            filterset = PermisoFilterSet(self.request.GET or None, queryset=queryset)
            for obj in filterset:
                object_list.append(obj)
        else:
            raise Http404()

        context = self.get_context_data(object_list=object_list)
        if request.user in direccion:
            context['direccion']= True

        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(PermisoDireccionEjecutivaListView, self).get_context_data(**kwargs)
        context['filterset'] = PermisoFilterSet(self.request.GET or None)
        context['url_destino'] = 'procesar-direccion-ejecutiva/'
        return context

class PermisoDireccionGestionListView(ListView):
    model = Permiso
    paginate_by = 7
    #template_name = 'permiso/permiso_direccion_list.html'

    def get(self, request, *args, **kwargs):
        super(PermisoDireccionGestionListView, self).get(request, *args, **kwargs)
        gestion = Group.objects.get(name="Dirección de Gestión").user_set.all()
        object_list = []

        if request.user in gestion:
            queryset = Permiso.objects.filter(
                enviado=True,
                enviado_para='Gestion',
            )|Permiso.objects.filter(
                Q(enviado = True),
                Q(revisado=True),
                Q(aprobado = True)
                |Q(aprobado=False)
            ).order_by('inicio')

            filterset = PermisoFilterSet(self.request.GET or None, queryset=queryset)
            for obj in filterset:
                object_list.append(obj)

        else:
             raise Http404()
        context = self.get_context_data(object_list=object_list)
        if request.user in gestion :
            context['gestion']= True
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(PermisoDireccionGestionListView, self).get_context_data(**kwargs)
        context['filterset'] = PermisoFilterSet(self.request.GET or None)
        context['url_destino'] = 'procesar-direccion-gestion/'
        return context


# lista todos los permisos dependientes:
class PermisoDependienteListView(ListView):
    model = Permiso
    paginate_by = 7
    #template_name = 'permiso/permiso_direccion_list.html'

    def get(self, request, *args, **kwargs):
        super(PermisoDependienteListView, self).get(request, *args, **kwargs)
        trabajador = Group.objects.get(name="Trabajador").user_set.all()
        object_list = []

        if self.request.user in trabajador:

            #traeme todos los permisos dirigidos que dependen para el envio a los tres primeros
            permisos1 = Permiso.objects.filter(
                Q(enviado=True),
                Q(enviado_para='Suplente'),
                Q(revisado = False),
                #Q(suplente = self.request.user),
            ).values_list('solicitante')

            #dime que equipos coinciden con el usuario loguedo y el solicitante
            equipos_incidentes = EquipoTrabajo.objects.filter(
                Q(integrante__in = permisos1),
                Q(cara_visible = request.user)|
                Q(director_proyecto = request.user)
            ).values_list('integrante')

            permisos = Permiso.objects.filter(
                Q(enviado=True),
                Q(revisado = False),
                Q(enviado_para='Suplente'),
                Q(solicitante__in = equipos_incidentes)|
                Q(suplente = request.user),
            ).exclude(
                Q(solicitante = request.user),
            )
            #retorname todos los permisos incidentes en los que yo me encuentre
            #pero a su vez que no estén procesados

            cv_dp = EquipoTrabajo.objects.filter(
                Q(integrante__in = permisos1),
                Q(cara_visible = request.user)|
                Q(director_proyecto = request.user)
            ).values_list('cara_visible', 'director_proyecto')

            filterset = Permisos_suplenteFilterSet(self.request.GET or None, queryset=permisos)

            for obj in filterset:
                p = Permiso.objects.get(pk = obj.pk)
                lista_p = []
                lista_p.append(p.solicitante)
                lista_p.append(0)

                cv_dp = EquipoTrabajo.objects.filter(
                    Q(integrante__in = list(lista_p)),
                ).values_list('cara_visible', 'director_proyecto')

                object_list.append(obj)
                #for i in cv_dp:
                #    print u'i'
                #    print i
                #    #aqui lo que hago es verificar si ya está aprobado por mi, siendo cara visible o
                #    #director de proyecto, entonces no lo muestro en la lista:
                #    if obj.aprobado_cv != None and i[0] == self.request.user:
                #        object_list.append(obj)
                #    elif obj.aprobado_dp != None and i[1] == self.request.user:
                #        object_list.append(obj)
                #    else:
                #        pass
            print object_list

        else:
             raise Http404()
        context = self.get_context_data(object_list=object_list)
        if request.user in trabajador:
            context['suplente']= True
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(PermisoDependienteListView, self).get_context_data(**kwargs)
        context['filterset'] = Permisos_suplenteFilterSet(self.request.GET or None)
        context['url_destino'] = 'procesar-dependiente/'
        return context


class AusentesListView(ListView):
    model = Permiso
    paginate_by = 7
    template_name = '/permiso/templates/permisos/permisos_ausentes_list.html'

    def get(self, request, *args, **kwargs):
        trabajador = Group.objects.get(name="Trabajador").user_set.all()
        if self.request.user in trabajador:
            super(AusentesListView, self).get(request, *args, **kwargs)
            queryset = Permiso.objects.filter(aprobado = True).order_by('inicio')
            template_name = '/permiso/templates/permisos/permisos_ausentes_list.html'
            filterset = Permisos_ausentesFilterSet(self.request.GET or None, queryset=queryset)
            object_list = []

            ahora = timezone.now()
            ahora.astimezone(timezone.utc).replace(tzinfo=None)

            for obj in filterset:
                if obj.inicio < ahora:
                    if obj.fin > ahora:
                        object_list.append(obj)

            context = self.get_context_data(object_list=object_list)
            context['listar_ausentes'] = True
            return self.render_to_response(context)
        else:
            raise Http404()

    def get_context_data(self, **kwargs):
        context = super(AusentesListView, self).get_context_data(**kwargs)
        context['filterset'] = Permisos_usuarioFilterSet(self.request.GET or None)
        return context



def VerObservaciones(request, pk):
    p = Permiso.objects.get(id = pk)

    presidencia = Group.objects.get(name="Presidencia").user_set.all()
    gestion = Group.objects.get(name="Dirección de Gestión").user_set.all()
    direccion = Group.objects.get(name="Dirección Ejecutiva").user_set.all()
    talento = Group.objects.get(name="Talento Humano").user_set.all()
    trabajador = Group.objects.get(name="Trabajador").user_set.all()

    l_direccion = []
    l_trabajador = []
    l_talento = []
    l_gestion = []
    l_presidencia= []
    if (
        request.user != p.solicitante
        and not(request.user in presidencia)
        and not(request.user in gestion)
        and not(request.user in talento)
        and not(request.user in direccion)
    ):
        raise Http404()
    if request.user in presidencia:
        o_presidencia = Observaciones.objects.filter(
            Q(fk_permiso = pk),
            Q(para = 'Presidencia'),
        )
        for i in o_presidencia:
            l_presidencia.append(i.pk)
    if request.user in gestion:
        o_gestion = Observaciones.objects.filter(
            Q(fk_permiso = pk),
            Q(para = 'Gestion')
        )
        for i in o_gestion:
            l_gestion.append(i.pk)
    if request.user in direccion:
        o_direccion = Observaciones.objects.filter(
            fk_permiso = pk,
            para = 'Direccion'
        )
        for i in o_direccion:
            l_direccion.append(i.pk)
    if request.user in talento:
        o_talento = Observaciones.objects.filter(
            Q(fk_permiso = pk),
            Q(para = 'Talento')
        )
        for i in o_talento:
            l_talento.append(i.pk)
    if request.user in trabajador:
        o_trabajador = Observaciones.objects.filter(
            fk_permiso = pk,
            para = 'Trabajador'
        )
        for i in o_trabajador:
            l_trabajador.append(i.pk)



    o = Observaciones.objects.filter(
        Q(pk__in=l_direccion)|
        Q(pk__in=l_talento)|
        Q(pk__in=l_gestion)|
        Q(pk__in=l_presidencia)|
        Q(pk__in=l_trabajador)
    )
    return render_to_response('permisos/observaciones_listar.html', {'object_list':o })



def ProcesarDependienteUpdateView(request, pk):
    permiso = Permiso.objects.get(id = pk)


    if request.POST:


        equipos_incidentes = EquipoTrabajo.objects.filter(
            Q(integrante = permiso.solicitante),
            Q(cara_visible = request.user)|
            Q(director_proyecto = request.user)
        ).values_list('cara_visible', 'director_proyecto')
        decision = request.POST.get('decision')
        print equipos_incidentes


        ########################################################
        #traeme todos los permisos dirigidos que dependen para el envio a los tres primeros
        permisos1 = Permiso.objects.filter(
            Q(enviado=True),
            Q(enviado_para='Suplente'),
            Q(revisado = False),
            #Q(suplente = self.request.user),
        ).values_list('solicitante')

        #dime que equipos coinciden con el usuario loguedo y el solicitante
        equipos_incidentes = EquipoTrabajo.objects.filter(
            Q(integrante__in = permisos1),
            Q(cara_visible = request.user)|
            Q(director_proyecto = request.user)
        ).values_list('integrante')

        permisos = Permiso.objects.filter(
            Q(enviado=True),
            Q(revisado = False),
            Q(enviado_para='Suplente'),
            Q(solicitante__in = equipos_incidentes)|
            Q(suplente = request.user),
        ).exclude(
            Q(solicitante = request.user),
        )
        #retorname todos los permisos incidentes en los que yo me encuentre
        #pero a su vez que no estén procesados
        #######################################################


        if not decision:
            raise ValueError('ERROR Elija una opcion') # arreglar para que de error de validación


        if decision == 'True':
            if (
                permiso.aprobado_suplente == None
                and permiso.suplente == request.user
            ):
                print permiso
                permiso.aprobado_suplente = True
                permiso.save()


            equipos = EquipoTrabajo.objects.filter(integrante__id = permiso.solicitante.id)
            for i in equipos:
                print i.integrante.all()
                if (
                    permiso.aprobado_cv == None
                    and request.user == i.cara_visible
                ):
                    permiso.aprobado_cv = True
                    permiso.aprobado_cv_por = request.user
                if (
                    permiso.aprobado_dp == None
                    and request.user == i.director_proyecto
                ):
                    permiso.aprobado_dp = True
                    permiso.aprobado_dp_por = request.user


                #si el permiso ya ha sido aprobado por un director de proyecto
                #se procede a ser aprobado por un segundo director de proyecto
                #para asi ser enviado directamente a Talento Humano:
                if (
                    permiso.aprobado_dp == True
                    and permiso.aprobado_dp_por != request.user
                    and request.user == i.director_proyecto
                ):
                    permiso.aprobado_dp_dos = True
                    permiso.aprobado_dp_dos_por = request.user

                #si el petmiso es aprobado por un cara visible que es el
                #mismo dp entonces pasa directamente a TH
                #if (
                #    (
                #        permiso.aprobado_dp != None and permiso.aprobado_cv != None
                #    )or
                #    (
                #        permiso.aprobado_dp != None and permiso.aprobado_dp_dos != None
                #    )
                #):
                #    break
            #########################3


            # si no tiene suplente el permiso entonces es aprobado por el suplente
            # automaticamente
            if permiso.aprobado_suplente == None and permiso.suplente == None:
                permiso.aprobado_suplente = True

            # si los tres están aprobados pasalo a talento humano
            enviar_talento = False
            if (
                permiso.aprobado_dp == True and permiso.aprobado_cv == True
                and permiso.aprobado_suplente == True and permiso.enviado_para == 'Suplente'
            ):
                permiso.enviado_para = 'Talento'
                enviar_talento = True
            if (
                permiso.aprobado_dp == True and permiso.aprobado_dp_dos == True
                and permiso.aprobado_suplente == True
                and permiso.enviado_para == 'Suplente'
            ):
                permiso.enviado_para = 'Talento'
                enviar_talento = True

            if (enviar_talento):

                talento = User.objects.filter(groups__name="Talento Humano")
                lista= []
                for i in talento:
                    lista.append(str(i.email))

                mensaje1 = (
                    "El permiso solicitado por " + str(permiso.solicitante) + " el " + str(permiso.fecha_solicitud)
                    + " para el dia " + str(permiso.inicio) + " hasta el " + str(permiso.fin)
                    + " ha sido enviado a Talento Humano para su revsión\nPara mas información entrar a konekata."
                )
                menssage_talento = (
                    'Solicitud de Permiso',
                    mensaje1,
                    "pdonaire1@gmail.com",
                    lista
                )
                mensaje2 = (
                    "El permiso solicitado el " + str(permiso.fecha_solicitud)
                    + " para el dia " + str(permiso.inicio) + " hasta el " + str(permiso.fin)
                    + " ha sido enviado a Talento Humano para su revsión\nPara mas información entrar a konekata "
                )
                menssage_solicitante = (
                    "Solicitud de Permiso",
                    mensaje2,
                    "pdonaire1@gmail.com",
                    [permiso.solicitante.email]
                )
                try:
                    send_mass_mail((menssage_talento, menssage_solicitante), fail_silently=False)
                except:
                    pass
                #
                #mensaje = (
                #    "El permiso solicitado el " + str(permiso.fecha_solicitud)
                #    + " para el dia " + str(permiso.inicio) + " hasta el " + str(permiso.fin)
                #    + " ha sido enviado a Talento Humano para su revsión\nPara mas información entrar a konekata "
                #)
                #asunto = "Solicitud de Permiso"
                #send_mail(
                #    asunto, mensaje, DEFAULT_FROM_EMAIL,
                #    [permiso.solicitante.email], fail_silently=False
                #)


            permiso.save()
            #_________Hasta aqui esta bien revisar la parte comentada____

        elif decision == 'False':
            if (
                permiso.aprobado_suplente == None
                and permiso.suplente == request.user
            ):
                permiso.aprobado_suplente = False
                permiso.save()

            equipos = EquipoTrabajo.objects.filter(integrante__id = permiso.solicitante.id)
            for i in equipos:
                if (
                    permiso.aprobado_cv == None
                    and request.user == i.cara_visible
                ):
                    permiso.aprobado_cv = False
                    permiso.aprobado_cv_por = request.user
                    break
                if (
                    permiso.aprobado_dp == None
                    and request.user == i.director_proyecto
                ):
                    permiso.aprobado_dp = False
                    permiso.aprobado_dp_por = request.user
                    break
                #si el permiso ya ha sido aprobado por un director de proyecto
                #se procede a ser NEGADO por un segundo director de proyecto
                #para asi ser enviado directamente a Talento Humano:
                if (
                    permiso.aprobado_dp == True
                    and permiso.aprobado_dp_por != request.user
                    and request.user == i.director_proyecto
                ):
                    permiso.aprobado_dp_dos = False
                    permiso.aprobado_dp_dos_por = request.user
                    break

            # si alguno está negado muere el permiso
            if (
                permiso.aprobado_dp == False or permiso.aprobado_cv == False
                or permiso.aprobado_suplente == False or permiso.aprobado_dp_dos == False
            ):
                permiso.aprobado = False
                permiso.revisado = True
                permiso.enviado = True
                mensaje = (
                    "El permiso solicitado el " + str(permiso.fecha_solicitud)
                    + " para el dia " + str(permiso.inicio) + " hasta el " + str(permiso.fin)
                    + " Con el motivo de: \"" + str(permiso.observacion) + "\" No ha podido ser enviado a Talento Humano debido a la negación por parte de algún cara visible, director de proyecto o por el suplente. \nPara mas información entrar a konekata "
                )
                asunto = "Solicitud de Permiso"
                try:
                    send_mail(
                        asunto, mensaje, DEFAULT_FROM_EMAIL,
                        [permiso.solicitante.email], fail_silently=False
                    )
                except:
                    pass
            permiso.save()
            #_________Hasta aqui esta bien____________

        #······································


        """
        asunto ="asunto"
        mensaje ="mensaje"
        mail = EmailMessage(asunto, mensaje, to=['pdonaire1@gmail.com'])
        mail.send()
        """
        #······································

        return redirect('/permiso/')
    else:

        #estamos en la vista y todavia no vamos a procesar...
        if (
            permiso.enviado_para == 'Suplente'
            and permiso.aprobado == False and permiso.enviado == True
            and permiso.revisado == False
            #and permiso.aprobado_suplente != False and permiso.aprobado_cv != False
            #and permiso.aprobado_dp != False and permiso.aprobado_dp_dos != False
        ):
            #si el permiso no ha sido aprobado por los tres primeros:
            if (request.user == permiso.suplente and permiso.aprobado_suplente == None):
                return render(request, 'permisos/procesar_dependientes.html',
                {
                    'object': permiso,
                })
            # fin aprobado supplente____________

            equipos = EquipoTrabajo.objects.filter(integrante__id = permiso.solicitante.id)
            for i in equipos:
                #print i.integrante.all()
                if (request.user == i.cara_visible and permiso.aprobado_cv == None):
                    return render(request, 'permisos/procesar_dependientes.html',
                    {
                        'object': permiso,
                    })
                if (request.user == i.director_proyecto and permiso.aprobado_dp == None):
                    return render(request, 'permisos/procesar_dependientes.html',
                    {
                        'object': permiso,
                    })
                if (
                    request.user == i.director_proyecto
                    and permiso.aprobado_dp == True
                    and permiso.aprobado_dp_por != request.user
                ):
                    return render(request, 'permisos/procesar_dependientes.html',
                    {
                        'object': permiso,
                    })

            #si no pertenece a ningun cv o d_p retorna 404
            raise Http404()

        else:
            raise ValueError('El permiso ya está procesado')
    raise Http404()





def ProcesarTalentoHumano(request, pk):
    permiso = Permiso.objects.get(pk = pk)

    talento = Group.objects.get(name="Talento Humano").user_set.all()

    """
        Si está logeado y:
            si el usuario actual es de talento humano o si el usuario act está en direccion
            o presidencia o si es el direcctor de proyecto del que necesita la aprobacion
            o si es el caravisible o si es el suplente puedes continuar.......
    """
    if ((request.user in talento) and (permiso.enviado_para == 'Talento')):

        if request.POST and permiso.revisado != True:

            decision = request.POST.get('decision')
            observacion = request.POST.get('observacion')
            para_post = request.POST.get('para')

            if not decision:
                raise ValueError('ERROR Elija una opcion') # arreglar para que de error de validación

            if (
                para_post == 'Gestion' or para_post == 'Presidencia' or para_post == 'Trabajador'
                or para_post == 'Direccion'or para_post == 'Talento'
            ):
                pass
            else:
                html="<html><p>Seleccione a quien va dirijida la observacion </p></html>"
                return HttpResponse(html)

            observaciones = Observaciones(
                observacion = observacion,
                fk_permiso = permiso,
                usuario = request.user,
                fecha_observacion = timezone.now(),
                para = para_post,
                fecha_creacion = permiso.fecha_edicion
            )
            #observaciones.save(commit=False)
            observaciones.save()
            if decision == 'True':

                permiso.aprobado = True
                permiso.revisado = True
                permiso.enviado = True
                permiso.aprobado_por = request.user#.username
                permiso.save()


            elif decision == 'False':

                permiso.aprobado = False
                permiso.revisado = True
                permiso.enviado = True
                permiso.aprobado_por = request.user#.username


                permiso.save()

            elif decision == 'Correccion':


                permiso.aprobado = None
                permiso.revisado = True
                permiso.enviado = False
                # y conserva el mismo enviado_para que el de antes...

                permiso.save()


            elif decision == 'env_presidencia':
                if (request.user in talento):
                    permiso.enviado_para = 'Presidencia'
                    #permiso.save()

            elif decision == 'env_direccion':
                if (request.user in talento):
                    permiso.enviado_para = 'Direccion'
                    #permiso.save()

            elif decision == 'env_gestion':
                if (request.user in talento):
                    permiso.enviado_para = 'Gestion'
            #······································
            mensaje = (
                "El permiso solicitado el " + str(permiso.fecha_solicitud)
                + " para el dia " + str(permiso.inicio) + " hasta el " + str(permiso.fin)
                + " Con el motivo de: \"" + str(permiso.observacion) + "\" ha sido procesado por talento humano\n"
                + ". \nPara mas información entrar a Konekata."
            )
            asunto = "Solicitud de Permiso"
            try:
                send_mail(
                    asunto, mensaje, DEFAULT_FROM_EMAIL,
                    [permiso.solicitante.email], fail_silently=False
                )
            except:
                pass
            #······································
            #observaciones.save()
            permiso.save()
            return redirect('/permiso/')
        else:
            """
            ***********************AQUI**ENTRA**POR**PRIMERA**VEZ*********************
            """
            #estamos en la vista y todavia no vamos a procesar...

            if (permiso.enviado_para == 'Talento' and permiso.revisado != True):

                return render(request, 'permisos/procesar.html', {
                    'object': permiso,
                    'MarcarCorreccion': True,
                    'TalentoHumano' : True,
                    #'formset': formset,
                })

            else:
                raise ValueError('No es suplente o permiso no enviado')
    else:
        html = "<html><body>El usuario logeado no posee permiso para entrar en esta sección.</body></html>"
        #return HttpResponse(html)
        raise Http404()






def ProcesarPresidencia(request, pk):
    permiso = Permiso.objects.get(pk = pk)

    presidencia = Group.objects.get(name="Presidencia").user_set.all()

    """
        Si está logeado y:
            si el usuario actual es de talento humano o si el usuario act está en direccion
            o presidencia o si es el direcctor de proyecto del que necesita la aprobacion
            o si es el caravisible o si es el suplente puedes continuar.......
    """
    if ((request.user in presidencia) and (permiso.enviado_para=="Presidencia")):

        if request.POST and permiso.revisado != True:

            decision = request.POST.get('decision')
            observacion = request.POST.get('observacion')
            para_post = request.POST.get('para')

            if not decision:
                raise ValueError('ERROR Elija una opcion') # arreglar para que de error de validación

            if (
                para_post == 'Gestion' or para_post == 'Presidencia' or para_post == 'Trabajador'
                or para_post == 'Direccion'or para_post == 'Talento'
            ):
                pass
            else:
                html="<html><p>Seleccione a quien va dirijida la observacion </p></html>"
                return HttpResponse(html)

            if decision == 'True':

                permiso.aprobado = True
                permiso.revisado = True
                permiso.enviado = True
                permiso.aprobado_por = request.user#.username
                permiso.save()

            elif decision == 'False':

                permiso.aprobado = False
                permiso.revisado = True
                permiso.enviado = True
                permiso.aprobado_por = request.user#.username
                permiso.save()

            elif decision == 'Correccion':

                permiso.aprobado = None
                permiso.revisado = True
                permiso.enviado = False
                # y conserva el mismo enviado_para que el de antes...

                permiso.save()

            else:
                raise (Http404())

            observaciones = Observaciones(
                observacion = observacion,
                fk_permiso = permiso,
                usuario = request.user,
                fecha_observacion = timezone.now(),
                para = para_post,
                fecha_creacion = permiso.fecha_edicion
            )
            #observaciones.save(commit=False)


            mensaje = (
                "El permiso solicitado el " + str(permiso.fecha_solicitud)
                + " para el dia " + str(permiso.inicio) + " hasta el " + str(permiso.fin)
                + " Con el motivo de: " + str(permiso.observacion)
                + ". A sido procesado por Presidencia.\nPara mas información entrar a konekata "
            )
            asunto = "Solicitud de Permiso"
            try:
                send_mail(
                    asunto, mensaje, 'pdonaire1@localhost',
                    [permiso.solicitante.email], fail_silently=False
                )
            except:
                pass
            #asunto = "Solicitud de Permiso CENDITEL"
            #mensaje = "El estatus y los datos del permiso son los siguientes: <br>Fecha:" + permiso.inicio + "fin: " + permiso.fin
            #mail = EmailMessage(asunto, mensaje, to=['pdonaire1@gmail.com'])
            #mail.send()
            #observaciones.save()
            observaciones.save()
            permiso.save()
            return redirect('/permiso/listar-presidencia')
        else:
            """
            ***********************AQUI**ENTRA**POR**PRIMERA**VEZ*********************
            """
            #estamos en la vista y todavia no vamos a procesar...

            if (permiso.enviado_para == 'Presidencia' and permiso.revisado != True):

                return render(request, 'permisos/procesar.html', {
                    'object': permiso,
                    'MarcarCorreccion': True,
                    #'formset': formset,
                })

            else:
                raise ValueError('No es suplente o permiso no enviado')
    else:
        html = "<html><body>El usuario logeado no posee permiso para entrar en esta sección.</body></html>"
        #return HttpResponse(html)
        raise Http404()


def ProcesarDireccionEjecutiva(request, pk):
    permiso = Permiso.objects.get(pk = pk)

    direccion = Group.objects.get(name="Dirección Ejecutiva").user_set.all()
    """
        Si está logeado y:
            si el usuario actual es de talento humano o si el usuario act está en direccion
            o presidencia o si es el direcctor de proyecto del que necesita la aprobacion
            o si es el caravisible o si es el suplente puedes continuar.......
    """
    if ((request.user in direccion) and (permiso.enviado_para=="Direccion")):

        if request.POST and permiso.revisado != True:

            decision = request.POST.get('decision')
            observacion = request.POST.get('observacion')
            para_post = request.POST.get('para')

            if not decision:
                raise ValueError('ERROR Elija una opcion') # arreglar para que de error de validación

            if (
                para_post == 'Gestion' or para_post == 'Presidencia' or para_post == 'Trabajador'
                or para_post == 'Direccion'or para_post == 'Talento'
            ):
                pass
            else:
                html="<html><p>Seleccione a quien va dirijida la observacion </p></html>"
                return HttpResponse(html)


            if decision == 'True':

                permiso.aprobado = True
                permiso.revisado = True
                permiso.enviado = True
                permiso.aprobado_por = request.user#.username
                permiso.save()

                #__________________________________________________________________


            elif decision == 'False':

                permiso.aprobado = False
                permiso.revisado = True
                permiso.enviado = True
                permiso.aprobado_por = request.user#.username


                permiso.save()

            elif decision == 'Correccion':


                permiso.aprobado = None
                permiso.revisado = True
                permiso.enviado = False
                # y conserva el mismo enviado_para que el de antes...

                permiso.save()

            else:
                raise (Http404())

            observaciones = Observaciones(
                observacion = observacion,
                fk_permiso = permiso,
                usuario = request.user,
                fecha_observacion = timezone.now(),
                para = para_post,
                fecha_creacion = permiso.fecha_edicion
            )
            #observaciones.save(commit=False)
            observaciones.save()
            permiso.save()

            mensaje = (
                "El permiso solicitado el " + str(permiso.fecha_solicitud)
                + " para el dia " + str(permiso.inicio) + " hasta el " + str(permiso.fin)
                + " Con el motivo de: \"" + str(permiso.observacion)
                + "\" A sido procesado por Drirección Ejecutiva.\nPara mas información entrar a konekata "
            )
            asunto = "Solicitud de Permiso"
            try:
                send_mail(
                    asunto, mensaje, DEFAULT_FROM_EMAIL,
                    [permiso.solicitante.email], fail_silently=False
                )
            except:
                pass
            return redirect('/permiso/listar-direccion/')
        else:
            """
            ***********************AQUI**ENTRA**POR**PRIMERA**VEZ*********************
            """
            #estamos en la vista y todavia no vamos a procesar...
            if (permiso.enviado_para == 'Direccion' and permiso.revisado != True):

                return render(request, 'permisos/procesar.html', {
                    'object': permiso,
                    'MarcarCorreccion': True,
                    #'formset': formset,
                })

            else:
                raise ValueError('No es suplente o permiso no enviado')
    else:
        html = "<html><body>El usuario logeado no posee permiso para entrar en esta sección.</body></html>"
        #return HttpResponse(html)
        raise Http404()





def ProcesarDireccionGestion(request, pk):
    permiso = Permiso.objects.get(pk = pk)

    gestion = Group.objects.get(name="Dirección de Gestión").user_set.all()
    """
        Si está logeado y:
            si el usuario actual es de talento humano o si el usuario act está en direccion
            o presidencia o si es el direcctor de proyecto del que necesita la aprobacion
            o si es el caravisible o si es el suplente puedes continuar.......
    """
    if ((request.user in gestion) and (permiso.enviado_para=="Gestion")):

        if request.POST and permiso.revisado != True:

            decision = request.POST.get('decision')
            observacion = request.POST.get('observacion')
            para_post = request.POST.get('para')

            if not decision:
                raise ValueError('ERROR Elija una opcion') # arreglar para que de error de validación

            if (
                para_post == 'Gestion' or para_post == 'Presidencia' or para_post == 'Trabajador'
                or para_post == 'Direccion'or para_post == 'Talento'
            ):
                pass
            else:
                html="<html><p>Seleccione a quien va dirijida la observacion </p></html>"
                return HttpResponse(html)


            if decision == 'True':

                permiso.aprobado = True
                permiso.revisado = True
                permiso.enviado = True
                permiso.aprobado_por = request.user#.username
                permiso.save()

                #__________________________________________________________________


            elif decision == 'False':

                permiso.aprobado = False
                permiso.revisado = True
                permiso.enviado = True
                permiso.aprobado_por = request.user#.username


                permiso.save()

            elif decision == 'Correccion':


                permiso.aprobado = None
                permiso.revisado = True
                permiso.enviado = False
                # y conserva el mismo enviado_para que el de antes...

                permiso.save()

            else:
                raise (Http404())

            observaciones = Observaciones(
                observacion = observacion,
                fk_permiso = permiso,
                usuario = request.user,
                fecha_observacion = timezone.now(),
                para = para_post,
                fecha_creacion = permiso.fecha_edicion
            )
            observaciones.save()
            permiso.save()

            mensaje = (
                "El permiso solicitado el " + str(permiso.fecha_solicitud)
                + " para el dia " + str(permiso.inicio) + " hasta el " + str(permiso.fin)
                + " Con el motivo de: \"" + str(permiso.observacion)
                + "\" A sido procesado por Drirección de Gestión.\nPara mas información entrar a konekata "
            )
            asunto = "Solicitud de Permiso"
            try:
                send_mail(
                    asunto, mensaje, DEFAULT_FROM_EMAIL,
                    [permiso.solicitante.email], fail_silently=False
                )
            except:
                pass
            return redirect('/permiso/listar-direccion-gestion/')
        else:
            """
            ***********************AQUI**ENTRA**POR**PRIMERA**VEZ*********************
            """
            #estamos en la vista y todavia no vamos a procesar...
            if (permiso.enviado_para == 'Gestion' and permiso.revisado != True):

                return render(request, 'permisos/procesar.html', {
                    'object': permiso,
                    'MarcarCorreccion': True,
                })

            else:
                raise ValueError('No es suplente o permiso no enviado')
    else:
        html = "<html><body>El usuario logeado no posee permiso para entrar en esta sección.</body></html>"
        #return HttpResponse(html)
        raise Http404()





def procesar(request, pk):
    permiso = Permiso.objects.get(pk = pk)

    talento = Group.objects.get(name="Talento Humano").user_set.all()
    direccion = Group.objects.get(name="Dirección Ejecutiva").user_set.all()
    gestion = Group.objects.get(name="Dirección de Gestión").user_set.all()
    presidencia = Group.objects.get(name="Presidencia").user_set.all()

    """
        Si está logeado y:
            si el usuario actual es de talento humano o si el usuario act está en direccion
            o presidencia o si es el direcctor de proyecto del que necesita la aprobacion
            o si es el caravisible o si es el suplente puedes continuar.......
    """
    if (
        request.user in talento or request.user in direccion or request.user in presidencia
        or permiso.equipo_trabajo.cara_visible == request.user
        or permiso.equipo_trabajo.director_proyecto == request.user
        or permiso.suplente == request.user
    ):
        if (
            (
                permiso.aprobado_suplente != None and permiso.suplente==request.user
                or (
                    permiso.aprobado_cv != None
                    and permiso.equipo_trabajo.cara_visible==request.user
                )
                or (
                    permiso.aprobado_dp != None
                    and permiso.equipo_trabajo.director_proyecto == request.user
                )
                or (
                    permiso.enviado_para == 'Suplente'
                    and permiso.solicitante == request.user
                )
           )
            and permiso.enviado_para=="Suplente"
        ):
            """
                AQUI LO QUE HAGO ES VERIFICAR SI EL PERMISO YA HA SIDO PROCESADO RETORNA 404
                Y TAMBIEN SI ESTÁ ENVIADO PARA SUPLENTE YO NO PUEDO ENTRAR A EL PORQUE SE
                SUPONE QUE AL HABER SIDO CREADO EL PERMISO, EL PERMISO YA FUE APROBADO POR
                CARA VISIBLE Y POR DIRECTOR DE PROYECTO SI YO SOY CV Y DP
            """
            print u'etntr'
            raise Http404()
        if permiso.revisado:
            html = "<html><body>El Permiso no se puede modificar porque ya está procesado.</body></html>"
            return HttpResponse(html)
        else:
            if request.POST:
                """
                ***************AQUI**RECOJO**LOS**DATOS*************
                """


                decision = request.POST.get('decision')
                observacion = request.POST.get('observacion')
                para_post = request.POST.get('para')


                #**************************************************************************
                if not decision:
                    raise ValueError('ERROR Elija una opcion') # arreglar para que de error de validación

                if (
                    para_post == 'Gestion' or para_post == 'Presidencia' or para_post == 'Trabajador'
                    or para_post == 'Direccion'or para_post == 'Talento'
                ):
                    """
                    if para_post == 'Gestion':
                        grupo = Group.objects.get(name='Dirección de Gestión')

                    elif para_post == 'Presidencia':
                        grupo = Group.objects.get(name = 'Presidencia')

                    elif para_post == 'Trabajador':
                        grupo = Group.objects.get(name = 'Trabajador')

                    elif para_post == 'Direccion':
                        grupo = Group.objects.get(name = 'Dirección Ejecutiva')
                    """



                elif permiso.enviado_para == 'Suplente':
                    pass
                else:
                    html="<html><p>Seleccione a quien va dirijida la observacion </p></html>"
                    pass#return HttpResponse(html)


                if decision == 'True':

                    if request.user in talento and permiso.enviado_para == 'Talento':
                        permiso.aprobado = True
                        permiso.revisado = True
                        permiso.enviado = True
                        permiso.aprobado_por = request.user#.username
                        permiso.save()
                    elif request.user in direccion and permiso.enviado_para == 'Direccion':
                        permiso.aprobado = True
                        permiso.revisado = True
                        permiso.enviado = True
                        permiso.aprobado_por = request.user#.username
                        permiso.save()
                    elif request.user in presidencia and permiso.enviado_para == 'Presidencia':
                        permiso.aprobado = True
                        permiso.revisado = True
                        permiso.enviado = True
                        permiso.aprobado_por = request.user#.username
                        permiso.save()
                    elif request.user in gestion and permiso.enviado_para == 'Gestion':
                        permiso.aprobado = True
                        permiso.revisado = True
                        permiso.enviado = True
                        permiso.aprobado_por = request.user#.username
                        permiso.save()
                    ## sin haber sido aprobado por los 3 primeros:
                    if (
                        permiso.aprobado_cv == None
                        and permiso.equipo_trabajo.cara_visible == request.user
                    ):
                        permiso.aprobado_cv = True
                    if (
                        permiso.aprobado_dp == None
                        and permiso.equipo_trabajo.director_proyecto == request.user
                    ):
                        permiso.aprobado_dp = True
                    if permiso.aprobado_suplente == None and permiso.suplente == request.user:
                        permiso.aprobado_suplente = True
                    elif permiso.aprobado_suplente == None and permiso.suplente == None:
                        permiso.aprobado_suplente = True

                    # si los tres están aprobados pasalo a talento humano
                    if (
                        permiso.aprobado_dp == True and permiso.aprobado_cv == True
                        and permiso.aprobado_suplente == True and permiso.enviado_para == 'Suplente'
                    ):
                        permiso.enviado_para = 'Talento'
                    # si alguno de los tres está negado entonces muere el permiso
                    elif (
                        permiso.aprobado_dp == False or permiso.aprobado_cv == False
                        or permiso.aprobado_suplente == False
                    ):
                        permiso.aprobado = False
                        permiso.revisado = True
                        permiso.enviado = True

                    permiso.save()
                    #__________________________________________________________________


                elif decision == 'False':

                    #cuando es enviado a suplente
                    if permiso.aprobado_suplente == None and permiso.suplente == request.user:
                        permiso.aprobado = False       #
                        permiso.enviado = True         #
                        permiso.revisado = True
                        permiso.aprobado_suplente == False
                        #Muere pero falta el save()
                    if (
                        permiso.aprobado_cv == None
                        and permiso.equipo_trabajo.cara_visible == request.user
                    ):
                        permiso.aprobado = False       #
                        permiso.enviado = True         #
                        permiso.revisado = True
                        permiso.aprobado_cv = False
                        #Muere
                    if (
                        permiso.aprobado_dp == None
                        and permiso.equipo_trabajo.director_proyecto == request.user
                    ):
                        permiso.aprobado = False       #
                        permiso.enviado = True         #
                        permiso.revisado = True
                        permiso.aprobado_dp = False
                        #Muere

                    #Hago que muera el permiso sin haber sido enviado a talento humano:
                    if (
                        permiso.aprobado_dp == False or permiso.aprobado_cv == False
                        or permiso.aprobado_suplente == False
                    ):

                        #########################
                        permiso.aprobado = False
                        permiso.revisado = True
                        permiso.enviado = True
                        permiso.aprobado_por = request.user#.username
                        #aqui falta un return

                    # si ya ha sido aprobado por los tre primeros
                    if (
                        (permiso.enviado_para == 'Talento' and request.user in talento)
                        or (permiso.enviado_para == 'Presidencia' and request.user in presidencia)
                        or (permiso.enviado_para == 'Direccion' and request.user in direccion)
                        or (permiso.enviado_para == 'Gestion' and request.user in gestion)
                    ):
                        permiso.aprobado = False
                        permiso.revisado = True
                        permiso.enviado = True
                        permiso.aprobado_por = request.user#.username


                    permiso.save()

                elif decision == 'Correccion':

                    if (
                        (request.user in talento and permiso.enviado_para == 'Talento')
                        or (request.user in direccion and permiso.enviado_para == 'Direccion')
                        or (request.user in presidencia and permiso.enviado_para == 'Presidencia')
                        or (request.user in gestion and permiso.enviado_para == 'Gestion')
                    ):
                        permiso.aprobado = None
                        permiso.revisado = True
                        permiso.enviado = False
                        # y conserva el mismo enviado_para que el de antes...

                    #permiso.save()

                elif decision == 'env_presidencia':
                    print u'algo'
                    if (request.user in talento):
                        permiso.enviado_para = 'Presidencia'
                        #permiso.save()

                elif decision == 'env_direccion':
                    if (request.user in talento):
                        permiso.enviado_para = 'Direccion'
                        #permiso.save()

                elif decision == 'env_gestion':
                    if (request.user in talento):
                        permiso.enviado_para = 'Gestion'

                permiso.save()
                observaciones = Observaciones(
                        observacion = observacion,
                        fk_permiso = permiso,
                        usuario = request.user,
                        fecha_observacion = timezone.now(),
                        para = para_post,
                        fecha_creacion = permiso.fecha_edicion
                    )
                observaciones.save()

                return redirect('/permiso/')
            else:
                """
                ***********************AQUI**ENTRA**POR**PRIMERA**VEZ*********************
                """
                #estamos en la vista y todavia no vamos a procesar...
                if (
                    permiso.enviado_para == 'Suplente'
                    and permiso.aprobado == False and permiso.enviado == True
                    and permiso.revisado == False
                ):
                    #si todavia no ha sido aprobado por los suplentes...


                    if permiso.suplente == request.user or permiso.aprobado_suplente == None:
                        #bandera = 0
                        #nombre = User.objects.get(username = permiso.solicitante)
                        #Nombre = nombre.first_name + ' '+ nombre.last_name
                        return render(request, 'permisos/procesar.html', {
                            'object': permiso,
                            #'Nombre':Nombre
                        })


                    elif permiso.equipo_trabajo.cara_visible == request.user and permiso.aprobado_cv == None:
                        return render(request, 'permisos/procesar.html', {
                            'object': permiso,
                        })
                    elif permiso.equipo_trabajo.director_proyecto == request.user and permiso.aprobado_dp == None:
                        return render(request, 'permisos/procesar.html', {
                            'object': permiso,
                        })
                    else:
                        raise ValueError('El permiso ya está procesado')
                elif (
                    permiso.enviado_para == 'Talento'
                    and request.user in talento
                ):
                    #Creo el formulario de observaciones con el formset
                    #ObservacionesFormSet = formset_factory(ObservacionesForm, extra=0, max_num=4, validate_max=True)
                    """
                    ObservacionesFormSet = inlineformset_factory(
                        Permiso,
                        Observaciones,
                        extra=0,
                        max_num=4,
                        validate_max=True
                    )

                    data = {
                        'form-TOTAL_FORMS': '1',
                        'form-INITIAL_FORMS': '0',
                        'form-MAX_NUM_FORMS': '4',
                        'form-0-title': '',
                        'form-0-pub_date': '',
                    }

                    #Form = modelform_factory(
                    #    Observaciones,
                    #    form=ObservacionesForm,
                    #    localized_fields=(
                    #        "observacion",
                    #        "para",
                    #    )
                    #)
                    #formset = ObservacionesFormSet(data)
                    formset = ObservacionesFormSet(
                        #request.GET,
                        instance=permiso
                    )

                    for form in formset:
                        print(form.as_table())
                    """
                    #formset.has_changed()
                    #print u'AQUIIII'

                    """
                    ArticleFormSet = formset_factory(ArticleForm, extra=3, max_num=1)
                    formset = ArticleFormSet()

                    for form in formset:
                        print(form.as_table())
                    """
                    return render(request, 'permisos/procesar.html', {
                        'object': permiso,
                        'MarcarCorreccion': True,
                        'TalentoHumano' : True,
                        #'formset': formset,
                    })

                elif (
                    permiso.enviado_para == 'Presidencia'
                    and request.user in presidencia
                ):
                    return render(request, 'permisos/procesar.html', {
                        'object': permiso,
                        'MarcarCorreccion': True,
                    })
                elif (
                    permiso.enviado_para == 'Direccion'
                    and request.user in direccion
                ):
                    return render(request, 'permisos/procesar.html', {
                        'object': permiso,
                        'MarcarCorreccion': True,
                    })
                elif (
                    permiso.enviado_para == 'Gestion'
                    and request.user in gestion
                ):
                    return render(request, 'permisos/procesar.html', {
                        'object': permiso,
                        'MarcarCorreccion': True,
                    })
                else:
                    raise ValueError('No es suplente o permiso no enviado')
    else:
        html = "<html><body>El usuario logeado no posee permiso para entrar en esta sección.</body></html>"
        #return HttpResponse(html)
        raise Http404()

#-----------------------------------------------------------------------------------------------

#------------------------------------------------------------------------------------------


#import simplejson

class ValidarFechas(TemplateView):

    def get(self, request, *arg, **kwarg):

        inicio = time.strptime(request.GET['ajax_inicio'], "%d/%m/%Y")
        print u'_______________________________________--'
        print inicio.weekday()
        inicio = request.GET['ajax_inicio']
        fin = request.GET['ajax_fin']
        lista = []


        print inicio.weekday()
        print u'_______________________________________--'
        if (inicio.weekday() == 5 or inicio.weekday() == 6 ):
            print u'pppppppppppppp'
            lista.append(False)
        else:
            print u'**************************************'
            lista.append(True)


        if (fin.weekday() == 5 or fin.weekday() == 6 ):
            lista.append(False)
        else:
            lista.append(True)
        data = {}
        data['inicio'] = lista[0]
        data['fin'] = lista[1]
        #data = serializers.serialize(
        #    'json',
        #    lista,
        #)
        #data = False;

        return HttpResponse(json.dumps(data), mimetype='application/json')
        data = serializers.serialize(
            'json',
            suplentes,
            fields=('id', 'username', 'first_name',)
        )

        return HttpResponse(data, mimetype='application/json')

class BusquedaAjaxView(TemplateView):

    def get(self, request, *args, **kwargs):

        inicio = request.GET['ajax_inicio']
        fin = request.GET['ajax_fin']

        permisos1 = Permiso.objects.filter(
                Q(aprobado=True)
            )& Permiso.objects.filter(
                Q(inicio__range = (inicio, fin))
                |Q(fin__range = (inicio, fin))
            )

        permisos2 = Permiso.objects.filter(
                Q(revisado=False),
                Q(enviado=True)
            )& Permiso.objects.filter(
                Q(inicio__range = (inicio, fin))
                |Q(fin__range = (inicio, fin))
            )
        suplentes = User.objects.exclude(
            Q(solicitante__in=list(permisos1))|
            Q(suplente__in=list(permisos1))
        )& User.objects.exclude(
            Q(solicitante__in=list(permisos2))|
            Q(suplente__in=list(permisos2))
        )& User.objects.exclude(
            Q(username = self.request.user)
        ).order_by('solicitante')



        data = serializers.serialize(
            'json',
            suplentes,
            fields=('id', 'username', 'first_name',)
        )

        return HttpResponse(data, mimetype='application/json')
















#@login_required
#def app_home(request):
#    template = "home.html"
#    return render_to_response(template, context_instance=RequestContext(request))


def inicio(request):
    form = AuthenticationForm()
    user = request.user
    if user:
        if user.is_active and user.is_superuser:
            return HttpResponseRedirect('/admin/')
    return render_to_response(
        'inicio.html',
        RequestContext(
            request, {'form':form}
        )
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
                    ctx = {"form":form, "mensaje": "User Inactivo"}
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

