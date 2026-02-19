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
    AnalisisSerializer, AnalisisArchivosSerializer
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
        analisis = Analisis.objects.filter(id_muestra_fk__id_caso_fk=caso)
        serializer = AnalisisSerializer(analisis, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def muestras(self, request, pk=None):
        """Obtener todas las muestras vinculadas a este caso"""
        caso = self.get_object()
        muestras = Muestra.objects.filter(id_caso_fk=caso)
        serializer = MuestraSerializer(muestras, many=True)
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
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============================================================================
# VISUALIZACIÓN DE MÁSCARAS
# ============================================================================

# Colores BGRA para cv2 (OpenCV usa BGR, no RGB)
COLORES_MASCARA = {
    'nucleo':      (0,   255,   0, 220),   # verde
    'micronucleo': (0,   0,   255, 255),   # rojo
    'membrana':    (255, 120,   0, 140),   # azul
}


def _extraer_dimensiones(objetos):
    """
    Recorre los objetos del JSON para encontrar el ancho y alto máximos.
    Se usa cuando el JSON no incluye width/height explícitos.
    """
    max_x, max_y = 0, 0
    for obj in objetos:
        for punto in obj.get('puntos', []):
            if punto[0] > max_x:
                max_x = punto[0]
            if punto[1] > max_y:
                max_y = punto[1]
    # +1 para que el píxel en max_x/max_y quede dentro del canvas
    return max_x + 1, max_y + 1


def renderizar_poligonos(objetos, tipos_visibles, ancho=None, alto=None):
    """
    Dibuja los polígonos del JSON sobre un canvas RGBA transparente.

    Estructura esperada del JSON:
        {
            "width": 1920,       # opcional pero recomendado
            "height": 1080,      # opcional pero recomendado
            "objetos": [
                {"id": 1, "tipo": "membrana", "puntos": [[x,y], [x,y], ...]},
                {"id": 2, "tipo": "nucleo",   "puntos": [[x,y], ...]},
                ...
            ]
        }

    Args:
        objetos        : lista de dicts con 'tipo' y 'puntos'
        tipos_visibles : lista de tipos a dibujar, ej. ['nucleo', 'membrana']
        ancho, alto    : dimensiones del canvas (se infieren si no se pasan)

    Returns:
        PIL.Image en modo RGBA
    """
    if not objetos:
        return None

    if ancho is None or alto is None:
        ancho, alto = _extraer_dimensiones(objetos)

    # Canvas transparente en formato BGRA para cv2
    canvas = np.zeros((alto, ancho, 4), dtype=np.uint8)

    # Orden de pintado: membrana primero (fondo), luego núcleo, luego micronúcleo (encima)
    orden = ['membrana', 'nucleo', 'micronucleo']
    # Agrupar objetos por tipo para pintarlos en orden correcto
    por_tipo = {t: [] for t in orden}
    for obj in objetos:
        tipo = obj.get('tipo')
        if tipo in por_tipo:
            puntos = obj.get('puntos', [])
            if puntos:
                por_tipo[tipo].append(np.array(puntos, dtype=np.int32))

    for tipo in orden:
        if tipo not in tipos_visibles:
            continue
        color = COLORES_MASCARA.get(tipo)
        if not color:
            continue
        for contorno in por_tipo[tipo]:
            cv2.fillPoly(canvas, [contorno], color)
            # Borde sutil para distinguir objetos adyacentes
            cv2.polylines(canvas, [contorno], isClosed=True, color=color[:3] + (255,), thickness=1)

    # cv2 trabaja en BGRA → convertir a RGBA para PIL
    canvas_rgba = cv2.cvtColor(canvas, cv2.COLOR_BGRA2RGBA)
    return Image.fromarray(canvas_rgba, 'RGBA')


def _obtener_archivo_activo(id_analisis):
    """Helper que devuelve el AnalisisArchivos activo o lanza DoesNotExist."""
    analisis = Analisis.objects.get(id_analisis=id_analisis)
    archivo = AnalisisArchivos.objects.get(id_analisis_fk=analisis, activo=True)
    return archivo


def _imagen_a_response(img: Image.Image) -> HttpResponse:
    """Convierte una PIL Image a HttpResponse PNG."""
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return HttpResponse(buffer.getvalue(), content_type='image/png')


@api_view(['GET'])
def obtener_mascara_png(request, id_analisis, tipo_mascara):
    """
    GET /api/analisis/{id}/mascara/{tipo}/
    tipo puede ser: nucleo | micronucleo | membrana | overlay

    - Para tipos individuales solo dibuja ese tipo.
    - Para 'overlay' dibuja todos los tipos en capas.
    """
    try:
        archivo = _obtener_archivo_activo(id_analisis)
    except Analisis.DoesNotExist:
        return HttpResponse("Análisis no encontrado", status=404)
    except AnalisisArchivos.DoesNotExist:
        return HttpResponse("No hay versión activa para este análisis", status=404)

    contenido = archivo.contenido_json
    objetos = contenido.get('objetos', [])
    ancho = contenido.get('width')
    alto = contenido.get('height')

    if tipo_mascara == 'overlay':
        tipos_visibles = list(COLORES_MASCARA.keys())
    elif tipo_mascara in COLORES_MASCARA:
        # Verificar que exista al menos un objeto de ese tipo
        existe = any(obj.get('tipo') == tipo_mascara for obj in objetos)
        if not existe:
            return HttpResponse(f"No hay objetos de tipo '{tipo_mascara}' en este análisis", status=404)
        tipos_visibles = [tipo_mascara]
    else:
        return HttpResponse(
            f"Tipo de máscara inválido. Usa: nucleo, micronucleo, membrana, overlay",
            status=400
        )

    img = renderizar_poligonos(objetos, tipos_visibles, ancho=ancho, alto=alto)

    if img is None:
        return HttpResponse("No hay objetos para renderizar", status=404)

    return _imagen_a_response(img)


@api_view(['GET'])
def obtener_json_activo(request, id_analisis):
    """
    GET /api/analisis/{id}/json-activo/
    Devuelve el AnalisisArchivos activo completo (incluyendo contenido_json).
    """
    try:
        archivo = _obtener_archivo_activo(id_analisis)
    except Analisis.DoesNotExist:
        return Response(
            {"detail": "Análisis no encontrado"},
            status=status.HTTP_404_NOT_FOUND
        )
    except AnalisisArchivos.DoesNotExist:
        return Response(
            {"detail": "No existe JSON activo para este análisis"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = AnalisisArchivosSerializer(archivo)
    return Response(serializer.data)