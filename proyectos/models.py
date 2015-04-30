# -*- coding: utf-8 -*-
from datetime import datetime
from django.db import models
from django.core.validators import MaxLengthValidator
from django.contrib.auth.models import User, Group
from permisos.models import *
# Create your models here.

class Proyecto(models.Model):
    nombre = models.CharField(
        'Nombre del Proyecto',
        max_length=200
    )
    descripcion = models.TextField(
        'Descripción',
        max_length = 2000,
        blank = True,
        null = True
    )
    class Meta:
        ordering = ["nombre"]
    
    def __unicode__(self):
        return unicode(self.nombre)

class EquipoTrabajo(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(
        'Descripción',
        max_length = 2000,
        blank = True,
        null = True
    )
    cara_visible = models.ForeignKey(
        User,
        related_name='cara_visible',
    )
    director_proyecto = models.ForeignKey(
        User,
        related_name='director_proyecto',
    )
    proyecto = models.ForeignKey(
        Proyecto,
        related_name='proyecto',
    )
    integrante = models.ManyToManyField(
        User,
        'Integrantes del Proyecto',
        related_name='integrante',
    )
    
    class Meta:
        ordering = ["nombre"]
    
    def __unicode__(self):
        return unicode(self.nombre)
