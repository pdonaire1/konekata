# -*- coding: utf-8 -*-
#from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
#from permisos.models import Permiso

User.add_to_class('direccion', models.TextField('Dirección',null=True,blank=True))
User.add_to_class('telefono', models.PositiveIntegerField('Teléfono',null=True,blank=True))
User.add_to_class('ci', models.PositiveIntegerField('Cédula de Identidad',null=True, blank=True))
#User.add_to_class('rol', models.IntegerField(null=False,blank=False, choices=ROLES))
# EN EL ROL 1: TRABAJADOR NORMAL, 2: ..., 3:.... Chequear la parte de permisoso del primer link
# PARA INFORMACION DE LOS ATRIBUTOS Y METODOS DE USER
# http://librosweb.es/libro/django_1_0/capitulo_12/utilizando_usuarios.html
# http://django.es/blog/metodos-para-crear-perfiles-de-usuario/

#PARA AGREGAR MÉTODOS A USER:::
# User.add_to_class('nombre_metodo', nombre_metodo)
# ahora podemos acceder al método mediante user.es_popular()


#class Bandejas (models.Model, Permiso, Actividad):
#    
#    #entradas = Permiso.
#    # procesados {negados, aprobados}
#    #
#    
#    
#    
#    
#    def entrada (self):
#        p = Permiso.objects.all().exclude(visto = True).order_by('fecha_solicitud').values()
#        a = Actividad.objects.all.exclude(visto = True).values()
#        
#        
#        return (a+p)
#    def __unicode__(self):
#        pass
#    
#        
    
#_________TAMBIEN_SE_PUEDE_DEFINIR_ASÍ__________
#class Usuario (User):
#    dni = models.IntegerField(max_length=8)
#    
#    class Meta:
#        ordering = ["dni"]
#    
#    def __unicode__(self):
#        return unicode(self.dni)