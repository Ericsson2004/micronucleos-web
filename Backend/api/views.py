from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.base import ContentFile
from .models import (
    Paciente, CasoClinico, Muestra, Analisis, 
    AnalisisEdicion, AnalisisResultados, AnalisisArchivos
)
from .serializers import (
    PacienteSerializer, CasoClinicoSerializer, MuestraSerializer,
    AnalisisSerializer, AnalisisEdicionSerializer
)

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


class AnalisisEdicionViewSet(viewsets.ModelViewSet):
    queryset = AnalisisEdicion.objects.all()
    serializer_class = AnalisisEdicionSerializer

    def perform_create(self, serializer):
        # Asigna automáticamente el usuario actual de la petición
        serializer.save(usuario=self.request.user)


class MuestraCreateView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        serializer = MuestraSerializer(data=request.data)
        if serializer.is_valid():
            # Solo guardamos la muestra e imagen
            muestra = serializer.save()
            
            # Eliminamos toda la lógica de llamar_microservicio y creación de archivos
            # para que el registro sea puro y simple.
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============================================================================
# HELPERS ADICIONALES ÚTILES
# ============================================================================

def obtener_mascaras_analisis(analisis_id):
    """
    Helper para obtener las 3 máscaras de un análisis específico
    """
    from .models import AnalisisArchivos
    
    analisis = Analisis.objects.get(id_analisis=analisis_id)
    
    mascaras = {
        'nucleo': None,
        'micronucleo': None,
        'membrana': None
    }
    
    # Obtener cada máscara
    try:
        mascaras['nucleo'] = analisis.archivos.get(tipo='mascara_nucleo').ruta_archivo.path
    except AnalisisArchivos.DoesNotExist:
        pass
    
    try:
        mascaras['micronucleo'] = analisis.archivos.get(tipo='mascara_micronucleo').ruta_archivo.path
    except AnalisisArchivos.DoesNotExist:
        pass
    
    try:
        mascaras['membrana'] = analisis.archivos.get(tipo='mascara_membrana').ruta_archivo.path
    except AnalisisArchivos.DoesNotExist:
        pass
    
    return mascaras


# ============================================================================
# EJEMPLO DE VISTA PARA VISUALIZAR MÁSCARAS
# ============================================================================

import numpy as np
from PIL import Image
from django.http import HttpResponse
from rest_framework.decorators import api_view
import io

@api_view(['GET'])
def obtener_mascara_png(request, id_analisis, tipo_mascara):
    """
    Convierte una máscara .npy a imagen PNG y la devuelve.
    """
    try:
        from .models import Analisis, AnalisisArchivos
        
        analisis = Analisis.objects.get(id_analisis=id_analisis)
        
        # Mapeo de tipos
        tipo_map = {
            'nucleo': 'mascara_nucleo',
            'micronucleo': 'mascara_micronucleo',
            'membrana': 'mascara_membrana'
        }
        
        # CASO ESPECIAL: overlay (todas las máscaras superpuestas)
        if tipo_mascara == 'overlay':
            return generar_overlay_mascaras(analisis)
        
        # Obtener archivo específico
        if tipo_mascara not in tipo_map:
            return HttpResponse("Tipo de máscara inválido", status=400)
        
        archivo = analisis.archivos.get(tipo=tipo_map[tipo_mascara])
        mask = np.load(archivo.ruta_archivo.path)
        
        # Crear imagen PNG
        img = crear_imagen_desde_mascara(mask, tipo_mascara)
        
        # Convertir a bytes
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return HttpResponse(buffer.getvalue(), content_type='image/png')
        
    except Analisis.DoesNotExist:
        return HttpResponse("Análisis no encontrado", status=404)
    except AnalisisArchivos.DoesNotExist:
        return HttpResponse(f"Máscara {tipo_mascara} no encontrada", status=404)
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)


def crear_imagen_desde_mascara(mask, tipo):
    """Convierte array numpy a imagen PIL con colores específicos"""
    alto, ancho = mask.shape
    img = Image.new('RGBA', (ancho, alto), (0, 0, 0, 0))
    pixels = img.load()
    
    # Colores según tipo
    colores = {
        'nucleo': (76, 175, 80, 200),      # Verde
        'micronucleo': (244, 67, 54, 220),  # Rojo brillante
        'membrana': (33, 150, 243, 150)     # Azul semi-transparente
    }
    
    color = colores.get(tipo, (255, 255, 255, 200))
    
    for y in range(alto):
        for x in range(ancho):
            if mask[y, x] > 0:
                pixels[x, y] = color
    
    return img


def generar_overlay_mascaras(analisis):
    """Genera imagen con las 3 máscaras superpuestas"""
    from .models import AnalisisArchivos
    
    try:
        # Cargar las 3 máscaras
        mask_nucleo = None
        mask_micronucleo = None
        mask_membrana = None
        
        try:
            archivo_nucleo = analisis.archivos.get(tipo='mascara_nucleo')
            mask_nucleo = np.load(archivo_nucleo.ruta_archivo.path)
        except AnalisisArchivos.DoesNotExist:
            pass
        
        try:
            archivo_micro = analisis.archivos.get(tipo='mascara_micronucleo')
            mask_micronucleo = np.load(archivo_micro.ruta_archivo.path)
        except AnalisisArchivos.DoesNotExist:
            pass
        
        try:
            archivo_memb = analisis.archivos.get(tipo='mascara_membrana')
            mask_membrana = np.load(archivo_memb.ruta_archivo.path)
        except AnalisisArchivos.DoesNotExist:
            pass
        
        # Determinar tamaño
        if mask_nucleo is not None:
            alto, ancho = mask_nucleo.shape
        elif mask_micronucleo is not None:
            alto, ancho = mask_micronucleo.shape
        elif mask_membrana is not None:
            alto, ancho = mask_membrana.shape
        else:
            return HttpResponse("No hay máscaras disponibles", status=404)
        
        # Crear imagen RGBA
        img = Image.new('RGBA', (ancho, alto), (0, 0, 0, 0))
        pixels = img.load()
        
        for y in range(alto):
            for x in range(ancho):
                # Membrana primero (más transparente)
                if mask_membrana is not None and mask_membrana[y, x] > 0:
                    pixels[x, y] = (33, 150, 243, 100)  # Azul claro
                
                # Núcleo
                if mask_nucleo is not None and mask_nucleo[y, x] > 0:
                    pixels[x, y] = (76, 175, 80, 180)  # Verde
                
                # Micronúcleo (más opaco para destacar)
                if mask_micronucleo is not None and mask_micronucleo[y, x] > 0:
                    pixels[x, y] = (244, 67, 54, 220)  # Rojo brillante
        
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return HttpResponse(buffer.getvalue(), content_type='image/png')
        
    except Exception as e:
        return HttpResponse(f"Error generando overlay: {str(e)}", status=500)