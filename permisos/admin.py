# -*- coding: utf-8 -*-
from django.contrib import admin
from .models import Permiso
from .models import Observaciones
from proyectos.models import EquipoTrabajo
from proyectos.models import Proyecto
from actividades.models import Actividad, Entrada
admin.site.register(Permiso)
admin.site.register(Observaciones)
admin.site.register(Proyecto)
admin.site.register(EquipoTrabajo)
admin.site.register(Actividad)
admin.site.register(Entrada)