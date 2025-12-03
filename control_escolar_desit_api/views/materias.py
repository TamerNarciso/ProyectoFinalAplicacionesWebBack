from django.db.models import *
from django.db import transaction
from control_escolar_desit_api.serializers import *
from control_escolar_desit_api.models import *
from rest_framework import permissions
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from datetime import datetime # <--- IMPORTANTE: AGREGAR ESTO

# ... (Tus clases de Alumnos se quedan igual) ...

class MateriaAll(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        materias = Materia.objects.all().order_by("id")
        lista = MateriaSerializer(materias, many=True).data
        return Response(lista, 200)

class MateriaView(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    # Función auxiliar para convertir "11:00 AM" -> "11:00"
    def convertir_hora(self, hora_str):
        try:
            # Intenta convertir formato "11:00 AM" a objeto tiempo
            dt = datetime.strptime(hora_str, "%I:%M %p")
            # Lo regresa en formato 24hrs "11:00"
            return dt.strftime("%H:%M")
        except Exception:
            # Si falla (ya viene en 24h o es nulo), devolvemos lo que llegó
            return hora_str

    def get(self, request, *args, **kwargs):
        materia = get_object_or_404(Materia, id=request.GET.get("id"))
        materia_data = MateriaSerializer(materia, many=False).data
        return Response(materia_data, 200)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        print("Datos recibidos:", request.data)

        try:
            # 1. Convertir Horas (AM/PM a 24H)
            h_inicio = self.convertir_hora(request.data.get("hora_inicio"))
            h_fin = self.convertir_hora(request.data.get("hora_fin"))

            # 2. Obtener instancia del profesor
            id_maestro_request = request.data.get('profesor_id') 
            maestro_instancia = None
            if id_maestro_request:
                maestro_instancia = Maestros.objects.filter(id=id_maestro_request).first()
            
            # 3. Crear Materia
            materia = Materia.objects.create(
                nrc = request.data.get("nrc"),
                nombre = request.data.get("nombre"),
                seccion = request.data.get("seccion"),
                dias = request.data.get("dias"), 
                hora_inicio = h_inicio, # Usamos la hora convertida
                hora_fin = h_fin,       # Usamos la hora convertida
                salon = request.data.get("salon"),
                programa_educativo = request.data.get("programa_educativo"),
                creditos = request.data.get("creditos"),
                profesor = maestro_instancia 
            )
            
            materia.save()
            return Response({"message": "Materia creada exitosamente", "id": materia.id}, 201)

        except Exception as e:
            print("ERROR AL CREAR MATERIA:", str(e)) 
            return Response({"message": "Error en el servidor: " + str(e)}, 400)

    @transaction.atomic
    def put(self, request, *args, **kwargs):
        try:
            materia = get_object_or_404(Materia, id=request.data["id"])

            # Convertimos las horas también al editar
            h_inicio = self.convertir_hora(request.data.get("hora_inicio"))
            h_fin = self.convertir_hora(request.data.get("hora_fin"))

            materia.nrc = request.data.get("nrc")
            materia.nombre = request.data.get("nombre")
            materia.seccion = request.data.get("seccion")
            materia.dias = request.data.get("dias")
            materia.hora_inicio = h_inicio
            materia.hora_fin = h_fin
            materia.salon = request.data.get("salon")
            materia.programa_educativo = request.data.get("programa_educativo")
            materia.creditos = request.data.get("creditos")

            id_maestro = request.data.get('profesor_id')
            if id_maestro:
                maestro_instancia = get_object_or_404(Maestros, id=id_maestro)
                materia.profesor = maestro_instancia
            else:
                materia.profesor = None 

            materia.save()

            return Response({"message": "Materia actualizada correctamente", "materia": MateriaSerializer(materia).data}, 200)
        
        except Exception as e:
            print("ERROR AL ACTUALIZAR:", str(e))
            return Response({"message": str(e)}, 400)

    # (El método delete y ValidarNRC se quedan igual)
    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        materia = get_object_or_404(Materia, id=request.GET.get("id"))
        try:
            materia.delete()
            return Response({"details": "Materia eliminada exitosamente"}, 200)
        except Exception as e:
            return Response({"details": "No se pudo eliminar la materia", "error": str(e)}, 400)

class ValidarNRC(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        nrc = request.GET.get("nrc")
        if not nrc:
            return Response({"message": "Parámetro 'nrc' es requerido"}, 400)
        existe = Materia.objects.filter(nrc=nrc).exists()
        return Response({ "nrc": nrc, "existe": existe, "disponible": not existe }, 200)