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
from .services.segmentacion_client import llamar_microservicio

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
    """
    Vista personalizada para crear muestra Y llamar al microservicio de segmentación
    """
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        print("=" * 80)
        print("🔵 MuestraCreateView - Iniciando proceso")
        print(f"📥 Datos recibidos: {dict(request.data)}")
        print("=" * 80)
        
        try:
            # ✅ PASO 1: Validar y crear la muestra
            serializer = MuestraSerializer(data=request.data)
            
            if not serializer.is_valid():
                print(f"❌ Error de validación: {serializer.errors}")
                return Response({
                    "success": False,
                    "error": "Datos inválidos",
                    "detalles": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            muestra = serializer.save()
            print(f"✅ Muestra creada:")
            print(f"   - ID: {muestra.id_muestra}")
            print(f"   - Tipo: {muestra.tipo_muestra}")
            print(f"   - Imagen: {muestra.ruta_imagen.path}")

            # ✅ PASO 2: Llamar al microservicio FastAPI (o simulado)
            print(f"🔄 Llamando al microservicio de segmentación...")
            resultado = llamar_ microservicio(muestra.ruta_imagen.path)
            print(f"✅ Respuesta del microservicio:")
            print(f"   - Estado: {resultado.get('estado')}")
            print(f"   - Métricas: {resultado.get('metricas')}")

            # ✅ PASO 3: Crear análisis
            analisis = Analisis.objects.create(
                id_muestra_fk=muestra,
                version_modelo=resultado.get("version_modelo", "simulado_v1.0"),
                estado=resultado.get("estado", "listo")
            )
            print(f"✅ Análisis creado: ID={analisis.id_analisis}, Estado={analisis.estado}")

            # ✅ PASO 4: Guardar resultados en JSONB
            metricas = resultado.get("metricas", {})
    
            resultado_obj = AnalisisResultados.objects.create(
                id_analisis_fk=analisis,
                resultado_jsonb=metricas,  
                metadatos_jsonb=metadatos
            )
            
            # ✅ PASO 5: Guardar las 3 máscaras NPY
            mascaras = resultado.get("mascaras", {})  # Dict con las 3 rutas
            
            # Mapeo de tipos
            tipos_mascaras = {
                'nucleo': 'mascara_nucleo',
                'micronucleo': 'mascara_micronucleo',
                'membrana': 'mascara_membrana'
            }
            
            archivos_guardados = []
            
            for tipo_original, tipo_db in tipos_mascaras.items():
                ruta_npy = mascaras.get(tipo_original)
                
                if ruta_npy and os.path.exists(ruta_npy):
                    # Leer el archivo NPY
                    with open(ruta_npy, 'rb') as f:
                        archivo_obj = AnalisisArchivos.objects.create(
                            id_analisis_fk=analisis,
                            tipo=tipo_db
                        )
                        
                        # Guardar el archivo usando Django's File
                        from django.core.files import File
                        nombre_archivo = f"{tipo_original}.npy"
                        archivo_obj.ruta_archivo.save(nombre_archivo, File(f), save=True)
                        
                        archivos_guardados.append({
                            'tipo': tipo_db,
                            'id': archivo_obj.id_archivo,
                            'ruta': archivo_obj.ruta_archivo.name
                        })
                        
                        print(f"✅ Máscara {tipo_db} guardada: {archivo_obj.ruta_archivo.name}")
                else:
                    print(f"⚠️ No se encontró máscara para {tipo_original}")
            
            # ✅ PASO 6 (OPCIONAL): Guardar preview PNG
            preview_path = resultado.get("preview_png")
            if preview_path and os.path.exists(preview_path):
                with open(preview_path, 'rb') as f:
                    preview_obj = AnalisisArchivos.objects.create(
                        id_analisis_fk=analisis,
                        tipo='preview'
                    )
                    preview_obj.ruta_archivo.save('preview.png', File(f), save=True)
                    print(f"✅ Preview guardado: {preview_obj.ruta_archivo.name}")
            
            # ✅ RESPUESTA EXITOSA
            return Response({
                "success": True,
                "muestra_id": muestra.id_muestra,
                "analisis_id": analisis.id_analisis,
                "estado": analisis.estado,
                "mensaje": "Muestra creada y análisis procesado exitosamente",
                "metricas": metricas,
                "archivos": archivos_guardados,
                "total_mascaras": len(archivos_guardados)
            }, status=status.HTTP_201_CREATED)


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
from django.conf import settings
import os

def ver_mascara_overlay(request, id_analisis):
    """
    Genera una imagen PNG con las 3 máscaras superpuestas en colores diferentes
    """
    analisis = Analisis.objects.get(id_analisis=id_analisis)
    
    # Obtener las rutas de las máscaras
    mascaras = obtener_mascaras_analisis(id_analisis)
    
    # Cargar las 3 máscaras
    mask_nucleo = np.load(mascaras['nucleo']) if mascaras['nucleo'] else None
    mask_micronucleo = np.load(mascaras['micronucleo']) if mascaras['micronucleo'] else None
    mask_membrana = np.load(mascaras['membrana']) if mascaras['membrana'] else None
    
    # Asumir que todas tienen el mismo tamaño
    if mask_nucleo is not None:
        alto, ancho = mask_nucleo.shape
    else:
        return HttpResponse("No hay máscaras disponibles", status=404)
    
    # Crear imagen RGBA
    img = Image.new('RGBA', (ancho, alto), (0, 0, 0, 0))
    pixels = img.load()
    
    for y in range(alto):
        for x in range(ancho):
            # Membrana (verde, más transparente, se dibuja primero)
            if mask_membrana is not None and mask_membrana[y, x] > 0:
                pixels[x, y] = (0, 255, 0, 80)  # Verde semi-transparente
            
            # Núcleo (rojo)
            if mask_nucleo is not None and mask_nucleo[y, x] > 0:
                pixels[x, y] = (255, 0, 0, 160)  # Rojo
            
            # Micronúcleo (azul, más opaco para destacar)
            if mask_micronucleo is not None and mask_micronucleo[y, x] > 0:
                pixels[x, y] = (0, 0, 255, 200)  # Azul destacado
    
    response = HttpResponse(content_type="image/png")
    img.save(response, "PNG")
    return response


def ver_mascara_individual(request, id_analisis, tipo_mascara):
    """
    Visualizar una máscara específica
    tipo_mascara: 'nucleo', 'micronucleo', 'membrana'
    """
    analisis = Analisis.objects.get(id_analisis=id_analisis)
    
    # Mapeo de tipos
    tipo_map = {
        'nucleo': 'mascara_nucleo',
        'micronucleo': 'mascara_micronucleo',
        'membrana': 'mascara_membrana'
    }
    
    if tipo_mascara not in tipo_map:
        return HttpResponse("Tipo de máscara inválido", status=400)
    
    try:
        archivo = analisis.archivos.get(tipo=tipo_map[tipo_mascara])
        mask = np.load(archivo.ruta_archivo.path)
        
        # Crear imagen
        img = Image.new('RGBA', (mask.shape[1], mask.shape[0]), (0, 0, 0, 0))
        pixels = img.load()
        
        # Color según tipo
        colores = {
            'nucleo': (255, 0, 0, 160),        # Rojo
            'micronucleo': (0, 0, 255, 200),   # Azul
            'membrana': (0, 255, 0, 100)       # Verde
        }
        
        color = colores[tipo_mascara]
        
        for y in range(mask.shape[0]):
            for x in range(mask.shape[1]):
                if mask[y, x] > 0:
                    pixels[x, y] = color
        
        response = HttpResponse(content_type="image/png")
        img.save(response, "PNG")
        return response
        
    except AnalisisArchivos.DoesNotExist:
        return HttpResponse(f"Máscara {tipo_mascara} no encontrada", status=404)