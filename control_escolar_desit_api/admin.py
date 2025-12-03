from django.contrib import admin
from django.utils.html import format_html
from control_escolar_desit_api.models import *

@admin.register(Administradores)
class AdministradoresAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "creation", "update")
    search_fields = ("user__username", "user__email", "user__first_name", "user__last_name")


@admin.register(Alumnos)
class AlumnosAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "creation", "update")
    search_fields = ("user__username", "user__email", "user__first_name", "user__last_name")


@admin.register(Maestros)
class MaestrosAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "creation", "update")
    search_fields = ("user__username", "user__email", "user__first_name", "user__last_name")


@admin.register(Materia)
class MateriaAdmin(admin.ModelAdmin):
    list_display = ("nrc", "nombre", "seccion", "profesor", "programa_educativo", "creditos")
    list_filter = ("programa_educativo",)
    search_fields = ("nrc", "nombre", "seccion", "profesor__user__first_name", "profesor__user__last_name")