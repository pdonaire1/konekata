# -*- coding: utf-8 -*-
from datetime import datetime
from django.db import models
from django.core.validators import MaxLengthValidator
from django.contrib.auth.models import User, Group
from proyectos.models import EquipoTrabajo

""" 
class Procesado(models.Model):
    usuario = models.ForeignKey(User)
    aprobado_cv = models.BooleanField(blank = True, null=True)
    aprobado_dp = models.BooleanField(blank = True, null=True)
    def __unicode__(self):
        return unicode(self.usuario)
""" 
class Permiso(models.Model):
    
    solicitante = models.ForeignKey(
        User,
        related_name='solicitante',
        )
    
    fecha_edicion = models.DateTimeField(
        auto_now=True,
        auto_now_add=True
        )
    
    fecha_solicitud = models.DateTimeField()
    
    
    inicio = models.DateTimeField(
        'Fecha y hora de inicio del permiso',
    )
    fin = models.DateTimeField(
        'Fecha y hora de culminación del permiso',
    )
    
    #tiempo_solicitado = models.TimeField() #HORAS
    
    observacion = models.TextField(
        'Observaciones',
        help_text = 'Ej. Asuntos personales',
        max_length="6000",
        validators=[MaxLengthValidator(5000)]
    )
    ##anexos##
    #anexos = models.FileField(upload_to='inicio/static/anexos', null = True )
    #ausencia = models.BooleanField() # 0: esta en el area de trabajo, 1: se encuntra ausente
    anexo_permiso = models.FileField(upload_to='anexos_permiso', null=True, blank=True )
    
    suplente = models.ForeignKey(
        User,
        related_name='suplente',
        blank=True,
        null=True
    )
    # revisado es qeuivalente a si está procesado
    revisado = models.NullBooleanField()
    
    aprobado_por = models.ForeignKey(
        User,
        related_name='aprobado_por',
        blank=True,
        null=True
    )

    aprobacion_a = models.BooleanField(
        default=False
    ) # 0:negado  1:aprobado

    aprobacion_b = models.BooleanField(
        default=False
    ) #solo para un segundo dp


    aprobado = models.NullBooleanField(
        null=True,
        blank=False,
    )
        # 0:negado  1:aprobado
    
    enviado = models.BooleanField(
        'Enviar',
        help_text = 'Si no está marcado, se guardará sin haber sido enviado',
    )

    aprobado_cv = models.NullBooleanField(
        blank = True,
        null = True,
    )
    aprobado_dp = models.NullBooleanField(
        blank = True,
        null = True,
    )
    #-----------------------------------------
    aprobado_dp_dos = models.NullBooleanField(
        blank = True,
        null = True,
    )
    #----------------------------------------
    aprobado_cv_por = models.ForeignKey(
        User,
        related_name='aprobado_cv_por',
        blank = True,
        null = True
    )
    aprobado_dp_por = models.ForeignKey(
        User,
        related_name='aprobado_dp_por',
        blank = True,
        null = True
    )
    aprobado_dp_dos_por = models.ForeignKey(
        User,
        related_name='aprobado_dp_dos_por',
        blank = True,
        null = True
    )
    
    
    
    #ap = models.
    #fixture-> para exportar los datos de la base de datos
    aprobado_suplente = models.NullBooleanField(
        blank = True,
        null = True,
    )
    CHAR_CHOICES = (
        ('Presidencia', 'Presidencia'),
        ('Gestion', 'Dirección de Gestión'),
        ('Direccion', 'Dirección Ejecutiva'),
        ('Talento', 'Talento Humano'),
        ('Suplente', 'Suplente'),
    )
    enviado_para = models.CharField(
        max_length = 12,
        choices = CHAR_CHOICES,
    )
    """
    #________________________________
    cv_dp = models.ManyToManyField(
        Procesado,
        related_name='procesado',
        blank=True,
        null=True
    )
    #________________________________
    """
    class Meta:
        ordering = ["fecha_solicitud"]
    
    def __unicode__(self):
        return unicode(self.pk)
    


class Observaciones(models.Model):
    observacion = models.TextField(
        'Agregar una observación',
        max_length="6000",
        validators=[MaxLengthValidator(5000)]
    )
    fk_permiso = models.ForeignKey(
        Permiso,
        related_name="fk_permiso",
    )
    usuario = models.ForeignKey(
        User,
        related_name='usuario',
    )
    fecha_observacion = models.DateTimeField(
        auto_now=True,
    )
    CHAR_CHOICES = (
        ('Presidencia', 'Presidencia'),
        ('Gestion', 'Dirección de Gestión'),
        ('Direccion', 'Dirección Ejecutiva'),
        ('Talento', 'Talento Humano'),
        ('Trabajador', 'Trabajador')
    )
    
    para = models.CharField(
        max_length = 12,
        choices = CHAR_CHOICES,
    )
    fecha_creacion = models.DateTimeField()#fecha de creación del permiso
    
    class Meta:
        ordering = ["fecha_observacion"]
    
    def __unicode__(self):
        return unicode(self.fk_permiso)

