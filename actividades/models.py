# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User, Group
from django.core.validators import MaxLengthValidator
import time

#def get_upload_file_name(intance, filename):
    #return "uploaded_files/%s_%s" % (str( time() ).replace('.','_'), filename)

class Actividad(models.Model):
    
    nombre = models.CharField(max_length="400")
    fecha_notificacion = models.DateTimeField(auto_now=True)#fecha en que se creó la actividad
    fecha_salida = models.DateTimeField('Comienzo de Actividad')#fecha de inicio de la actividad
    fecha_fin = models.DateTimeField('Culminación de Actividad')#fecha fin de la actividad
    
    informacion = models.TextField(
        'Agregar Información',
        max_length="6000",
        validators=[MaxLengthValidator(5000)]
    )
    
    inscritos = models.ManyToManyField(User, blank=True)
    #ultima_act = models.BooleanField(null = True, blank=True)
    
    anexo_actividad = models.FileField(upload_to='anexos_actividad', null=True, blank=True )
    
    def __unicode__(self):
        return unicode(self.nombre)


class Entrada(models.Model):
    fecha_ingreso = models.DateTimeField(blank=True, null=True)#fecha de ingreso
    usuario = models.ForeignKey(User)
    actividad = models.ForeignKey(Actividad)
    anexo_usuario = models.FileField('',upload_to='anexo_usuario', null=True, blank=True )
    def __unicode__(self):
        return unicode(self.usuario)