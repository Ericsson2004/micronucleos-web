from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import HttpResponse
from rest_framework.decorators import api_view
import numpy as np
from PIL import Image
import io
import cv2

from .models import (
    Paciente, CasoClinico, Muestra, Analisis,
    AnalisisResultados, AnalisisArchivos
)
from .serializers import (
    PacienteSerializer, CasoClinicoSerializer, MuestraSerializer,
    AnalisisSerializer,AnalisisArchivosSerializer
)

# ============================================================================
# VIEWSETS
# ============================================================================

class PacienteViewSet(viewsets.ModelViewSet):
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer
    
    @action(detail=True, methods=['get'])
    def casos(self, request, pk=None):
        """Obtener todos los casos de un paciente específico"""
        paciente = self.get_object()
        casos = paciente.casos.all()
        serializer = CasoClinicoSerializer(casos, many=True)
        return Response(serializer.data)


class CasoClinicoViewSet(viewsets.ModelViewSet):
    queryset = CasoClinico.objects.all()
    serializer_class = CasoClinicoSerializer
    
    @action(detail=True, methods=['get'])
    def analisis(self, request, pk=None):
        """Obtener todos los análisis vinculados a este caso"""
        caso = self.get_object()
        # Buscamos a través de las muestras del caso
        analisis = Analisis.objects.filter(id_muestra_fk__id_caso_fk=caso)
        serializer = AnalisisSerializer(analisis, many=True)
        return Response(serializer.data)


class MuestraViewSet(viewsets.ModelViewSet):
    queryset = Muestra.objects.all()
    serializer_class = MuestraSerializer
    parser_classes = (MultiPartParser, FormParser)


class AnalisisViewSet(viewsets.ModelViewSet):
    queryset = Analisis.objects.all()
    serializer_class = AnalisisSerializer
    
    @action(detail=True, methods=['post'])
    def cambiar_estado(self, request, pk=None):
        """Actualizar el estado del procesamiento de la IA"""
        analisis = self.get_object()
        nuevo_estado = request.data.get('estado')
        estados_validos = ['pendiente', 'proceso', 'listo', 'error']
        
        if nuevo_estado in estados_validos:
            analisis.estado = nuevo_estado
            analisis.save()
            return Response({'status': 'Estado actualizado'})
        return Response({'error': 'Estado no válido'}, status=status.HTTP_400_BAD_REQUEST)


class MuestraCreateView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        serializer = MuestraSerializer(data=request.data)
        if serializer.is_valid():
            muestra = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============================================================================
# VISUALIZACIÓN DE MÁSCARAS
# ============================================================================

def crear_imagen_desde_json(mask_json, tipo):
    alto = len(mask_json)
    ancho = len(mask_json[0])

    img = Image.new('RGBA', (ancho, alto), (0, 0, 0, 0))
    pixels = img.load()

    colores = {
        'nucleo': (0, 255, 0, 255),
        'micronucleo': (255, 0, 0, 255),
        'membrana': (0, 120, 255, 180),
    }

    color = colores[tipo]

    for y in range(alto):
        for x in range(ancho):
            if mask_json[y][x]:
                pixels[x, y] = color

    return img

@api_view(['GET'])
def obtener_mascara_png(request, id_analisis, tipo_mascara):
    try:
        analisis = Analisis.objects.get(id_analisis=id_analisis)

        archivo = AnalisisArchivos.objects.get(
            id_analisis_fk=analisis,
            activo=True
        )

        contenido = archivo.contenido_json

        if tipo_mascara not in contenido:
            return HttpResponse("Máscara no encontrada", status=404)

        img = crear_imagen_desde_json(
            contenido[tipo_mascara],
            tipo_mascara
        )

        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)

        return HttpResponse(buffer.getvalue(), content_type='image/png')

    except Analisis.DoesNotExist:
        return HttpResponse("Análisis no encontrado", status=404)
    except AnalisisArchivos.DoesNotExist:
        return HttpResponse("No hay versión activa", status=404)

def generar_overlay_mascaras(analisis):
    archivo = AnalisisArchivos.objects.get(
        id_analisis_fk=analisis,
        activo=True
    )

    contenido = archivo.contenido_json

    base = (
        contenido.get('nucleo')
        or contenido.get('micronucleo')
        or contenido.get('membrana')
    )

    if not base:
        return HttpResponse("No hay máscaras", status=404)

    alto = len(base)
    ancho = len(base[0])

    img = Image.new('RGBA', (ancho, alto), (0, 0, 0, 0))
    pixels = img.load()

    for y in range(alto):
        for x in range(ancho):
            if contenido.get('membrana') and contenido['membrana'][y][x]:
                pixels[x, y] = (0, 120, 255, 140)
            if contenido.get('nucleo') and contenido['nucleo'][y][x]:
                pixels[x, y] = (0, 255, 0, 220)
            if contenido.get('micronucleo') and contenido['micronucleo'][y][x]:
                pixels[x, y] = (255, 0, 0, 255)

    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    return HttpResponse(buffer.getvalue(), content_type='image/png')

@api_view(['GET'])
def obtener_json_activo(request, id_analisis):
    try:
        archivo = AnalisisArchivos.objects.get(
            id_analisis_fk=id_analisis,
            activo=True
        )
    except AnalisisArchivos.DoesNotExist:
        return Response(
            {"detail": "No existe JSON activo para este análisis"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = AnalisisArchivosSerializer(archivo)
    return Response(serializer.data)