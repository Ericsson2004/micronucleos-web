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
            resultado = llamar_microservicio(muestra.ruta_imagen.path)
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
            
            # Asegurar que metricas sea un dict, no un string vacío
            if not isinstance(metricas, dict):
                metricas = {}
                print("⚠️ Las métricas no son un dict, usando dict vacío")
            
            metadatos = {
                "fuente": "fastapi" if not resultado.get("simulado") else "simulado",
                "simulado": resultado.get("simulado", False),
                "timestamp_proceso": resultado.get("timestamp_proceso"),
                "version_modelo": resultado.get("version_modelo", "desconocido")
            }
            
            resultado_obj = AnalisisResultados.objects.create(
                id_analisis_fk=analisis,
                resultado_jsonb=metricas,  # ✅ Ahora tiene datos reales
                metadatos_jsonb=metadatos
            )
            print(f"✅ Resultados guardados:")
            print(f"   - ID: {resultado_obj.id_resultado}")
            print(f"   - Métricas: {metricas}")
            print(f"   - Metadatos: {metadatos}")

            # ✅ PASO 5: Guardar archivo .npy (máscara)
            archivo_npy_path = resultado.get("archivo_npy")
            
            if archivo_npy_path:
                # Si tenemos la ruta del archivo
                import os
                if os.path.exists(os.path.join('media', archivo_npy_path)):
                    archivo_obj = AnalisisArchivos.objects.create(
                        id_analisis_fk=analisis,
                        tipo="mascara",
                        ruta_archivo=archivo_npy_path
                    )
                    print(f"✅ Archivo máscara guardado:")
                    print(f"   - ID: {archivo_obj.id_archivo}")
                    print(f"   - Ruta: {archivo_npy_path}")
                else:
                    print(f"⚠️ Archivo .npy no encontrado en: {archivo_npy_path}")
            else:
                print("⚠️ No se recibió archivo .npy del microservicio")

            # ✅ RESPUESTA EXITOSA
            print("=" * 80)
            print("✅ Proceso completado exitosamente")
            print("=" * 80)
            
            return Response({
                "success": True,
                "muestra_id": muestra.id_muestra,
                "analisis_id": analisis.id_analisis,
                "estado": analisis.estado,
                "mensaje": "Muestra creada y análisis procesado exitosamente",
                "metricas": metricas,
                "tiene_mascara": bool(archivo_npy_path)
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            # ❌ MANEJO DE ERRORES
            import traceback
            error_trace = traceback.format_exc()
            print("=" * 80)
            print(f"❌ ERROR en MuestraCreateView:")
            print(error_trace)
            print("=" * 80)
            
            # Si se creó la muestra pero falló después, actualizar análisis a error
            try:
                if 'analisis' in locals():
                    analisis.estado = 'error'
                    analisis.save()
                    print(f"⚠️ Análisis marcado como error: ID={analisis.id_analisis}")
            except:
                pass
            
            return Response({
                "success": False,
                "error": "Error al procesar la muestra",
                "detalle": str(e),
                "tipo_error": type(e).__name__
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

import numpy as np
from PIL import Image
from django.http import HttpResponse
from django.conf import settings
import os

def ver_mascara_png(request, id_muestra):
    muestra = Muestra.objects.get(id_muestra=id_muestra)
    path_npy = os.path.join(settings.MEDIA_ROOT, muestra.archivo_npy.name)
    
    # Cargar el array
    mask = np.load(path_npy)
    
    # Crear imagen RGBA (Transparente)
    # Importante: mask.shape es (alto, ancho)
    img = Image.new('RGBA', (mask.shape[1], mask.shape[0]), (0,0,0,0))
    pixels = img.load()
    
    for y in range(mask.shape[0]):
        for x in range(mask.shape[1]):
            val = mask[y, x]
            if val == 1: # Núcleo
                pixels[x, y] = (255, 0, 0, 160) # Rojo semi-transparente
            elif val == 2: # Membrana
                pixels[x, y] = (0, 255, 0, 100) # Verde semi-transparente
    
    response = HttpResponse(content_type="image/png")
    img.save(response, "PNG")
    return response