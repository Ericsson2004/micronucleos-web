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
    AnalisisEdicion, AnalisisResultados, AnalisisArchivos
)
from .serializers import (
    PacienteSerializer, CasoClinicoSerializer, MuestraSerializer,
    AnalisisSerializer, AnalisisEdicionSerializer
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
            muestra = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============================================================================
# VISUALIZACIÓN DE MÁSCARAS
# ============================================================================

def normalizar_mascara(mask):
    if mask is None:
        return None

    # array 0-D → objeto real
    if isinstance(mask, np.ndarray) and mask.shape == ():
        mask = mask.item()

    # diccionario
    if isinstance(mask, dict):
        # Caso común: lista de máscaras
        if 'masks' in mask and isinstance(mask['masks'], (list, tuple)):
            if len(mask['masks']) > 0:
                mask = mask['masks'][0]

        # Caso común: mask directa
        elif 'mask' in mask:
            mask = mask['mask']

        # Caso genérico: primera ndarray válida
        else:
            for v in mask.values():
                if isinstance(v, np.ndarray):
                    mask = v
                    break

    # lista / tupla
    if isinstance(mask, (list, tuple)):
        mask = mask[0]

    # Validaciones finales
    if not isinstance(mask, np.ndarray):
        print(f"❌ Máscara inválida, tipo final: {type(mask)}")
        return None

    if mask.ndim != 2:
        print(f"❌ Máscara no es 2D: shape={mask.shape}")
        return None

    return mask

@api_view(['GET'])
def obtener_mascara_png(request, id_analisis, tipo_mascara):
    """
    Convierte una máscara .npy a imagen PNG y la devuelve.
    
    Parámetros:
    - id_analisis: ID del análisis
    - tipo_mascara: 'nucleo', 'micronucleo', 'membrana', 'overlay'
    
    Retorna: Imagen PNG con la máscara coloreada
    """
    print("🔥 ENTRÓ A obtener_mascara_png 🔥")

    print(f"\n{'='*60}")
    print(f"🔍 Solicitando máscara: id_analisis={id_analisis}, tipo={tipo_mascara}")
    
    try:
        analisis = Analisis.objects.get(id_analisis=id_analisis)
        print(f"✅ Análisis encontrado: {analisis}")
        
        # Mapeo de tipos
        tipo_map = {
            'nucleo': 'mascara_nucleo',
            'micronucleo': 'mascara_micronucleo',
            'membrana': 'mascara_membrana'
        }
        
        # CASO ESPECIAL: overlay (todas las máscaras superpuestas)
        if tipo_mascara == 'overlay':
            print("📊 Generando overlay combinado...")
            return generar_overlay_mascaras(analisis)
        
        # Validar tipo de máscara
        if tipo_mascara not in tipo_map:
            print(f"❌ Tipo de máscara inválido: {tipo_mascara}")
            return HttpResponse("Tipo de máscara inválido", status=400)
        
        tipo_bd = tipo_map[tipo_mascara]
        print(f"🔍 Buscando máscara tipo: {tipo_bd}")
        
        # Obtener archivo de la base de datos
        archivo = analisis.archivos.get(tipo=tipo_bd)
        print(f"✅ Archivo encontrado en BD: {archivo.ruta_archivo.path}")
        
        # Verificar que el archivo existe en disco
        import os
        if not os.path.exists(archivo.ruta_archivo.path):
            print(f"❌ El archivo no existe en disco: {archivo.ruta_archivo.path}")
            return HttpResponse("Archivo de máscara no encontrado en disco", status=404)
        
        print(f"✅ Archivo existe en disco")
        
        # ⭐ CARGAR CON allow_pickle=True
        mask = np.load(archivo.ruta_archivo.path, allow_pickle=True)
        mask = normalizar_mascara(mask)
        
        if mask is None:
            return HttpResponse("Máscara inválida", status=404)
        
        # Crear imagen PNG
        img = crear_imagen_desde_mascara(mask, tipo_mascara)
        print(f"✅ Imagen PNG creada")
        
        # Convertir a bytes
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        print(f"✅ Retornando imagen PNG ({len(buffer.getvalue())} bytes)")
        print(f"{'='*60}\n")
        
        return HttpResponse(buffer.getvalue(), content_type='image/png')
        
    except Analisis.DoesNotExist:
        print(f"❌ Análisis no encontrado: {id_analisis}")
        return HttpResponse("Análisis no encontrado", status=404)
    except AnalisisArchivos.DoesNotExist:
        print(f"❌ Máscara no encontrada en BD: tipo={tipo_mascara}")
        return HttpResponse(f"Máscara {tipo_mascara} no encontrada", status=404)
    except Exception as e:
        print(f"❌ Error inesperado: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return HttpResponse(f"Error: {str(e)}", status=500)


def crear_imagen_desde_mascara(mask, tipo):
    # 🧠 Engrosar la máscara (kernel 3x3)
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.dilate(mask.astype(np.uint8), kernel, iterations=1)

    alto, ancho = mask.shape
    img = Image.new('RGBA', (ancho, alto), (0, 0, 0, 0))
    pixels = img.load()

    colores = {
        'nucleo': (0, 255, 0, 255),        # Verde sólido
        'micronucleo': (255, 0, 0, 255),   # Rojo sólido
        'membrana': (0, 120, 255, 200)     # Azul visible
    }

    color = colores[tipo]

    for y in range(alto):
        for x in range(ancho):
            if mask[y, x] > 0:
                pixels[x, y] = color

    return img


def generar_overlay_mascaras(analisis):
    """
    Genera imagen PNG con las 3 máscaras superpuestas en diferentes colores.
    
    Parámetros:
    - analisis: Objeto Analisis
    
    Retorna: HttpResponse con imagen PNG
    """
    print(f"🎨 Generando overlay para análisis {analisis.id_analisis}")
    
    try:
        # Cargar las 3 máscaras
        mask_nucleo = None
        mask_micronucleo = None
        mask_membrana = None
        
        # NÚCLEO
        try:
            archivo_nucleo = analisis.archivos.get(tipo='mascara_nucleo')
            print(f"✅ Encontrado archivo núcleo: {archivo_nucleo.ruta_archivo.path}")
            mask_nucleo = np.load(archivo_nucleo.ruta_archivo.path, allow_pickle=True)
            mask_nucleo = normalizar_mascara(mask_nucleo)

            print(f"✅ Máscara núcleo cargada: shape={mask_nucleo.shape}, dtype={mask_nucleo.dtype}")
            
            # ⭐ VALIDAR QUE TENGA 2 DIMENSIONES
            if len(mask_nucleo.shape) != 2:
                print(f"❌ ERROR: Máscara núcleo tiene dimensiones incorrectas: {mask_nucleo.shape}")
                print(f"   Contenido: {mask_nucleo}")
                mask_nucleo = None
            elif mask_nucleo.shape[0] == 0 or mask_nucleo.shape[1] == 0:
                print(f"❌ ERROR: Máscara núcleo está vacía")
                mask_nucleo = None
                
        except AnalisisArchivos.DoesNotExist:
            print("⚠️ No hay máscara de núcleo en BD")
        except Exception as e:
            print(f"❌ Error cargando núcleo: {type(e).__name__}: {str(e)}")
        
        # MICRONÚCLEO
        try:
            archivo_micro = analisis.archivos.get(tipo='mascara_micronucleo')
            print(f"✅ Encontrado archivo micronúcleo: {archivo_micro.ruta_archivo.path}")
            mask_micronucleo = np.load(archivo_micro.ruta_archivo.path, allow_pickle=True)
            mask_micronucleo = normalizar_mascara(mask_micronucleo)

            print(f"✅ Máscara micronúcleo cargada: shape={mask_micronucleo.shape}, dtype={mask_micronucleo.dtype}")
            
            # ⭐ VALIDAR QUE TENGA 2 DIMENSIONES
            if len(mask_micronucleo.shape) != 2:
                print(f"❌ ERROR: Máscara micronúcleo tiene dimensiones incorrectas: {mask_micronucleo.shape}")
                print(f"   Contenido: {mask_micronucleo}")
                mask_micronucleo = None
            elif mask_micronucleo.shape[0] == 0 or mask_micronucleo.shape[1] == 0:
                print(f"❌ ERROR: Máscara micronúcleo está vacía")
                mask_micronucleo = None
                
        except AnalisisArchivos.DoesNotExist:
            print("⚠️ No hay máscara de micronúcleo en BD")
        except Exception as e:
            print(f"❌ Error cargando micronúcleo: {type(e).__name__}: {str(e)}")
        
        # MEMBRANA
        try:
            archivo_memb = analisis.archivos.get(tipo='mascara_membrana')
            print(f"✅ Encontrado archivo membrana: {archivo_memb.ruta_archivo.path}")
            mask_membrana = np.load(archivo_memb.ruta_archivo.path, allow_pickle=True)
            mask_membrana = normalizar_mascara(mask_membrana)

            print(f"✅ Máscara membrana cargada: shape={mask_membrana.shape}, dtype={mask_membrana.dtype}")
            
            # ⭐ VALIDAR QUE TENGA 2 DIMENSIONES
            if len(mask_membrana.shape) != 2:
                print(f"❌ ERROR: Máscara membrana tiene dimensiones incorrectas: {mask_membrana.shape}")
                print(f"   Contenido: {mask_membrana}")
                mask_membrana = None
            elif mask_membrana.shape[0] == 0 or mask_membrana.shape[1] == 0:
                print(f"❌ ERROR: Máscara membrana está vacía")
                mask_membrana = None
                
        except AnalisisArchivos.DoesNotExist:
            print("⚠️ No hay máscara de membrana en BD")
        except Exception as e:
            print(f"❌ Error cargando membrana: {type(e).__name__}: {str(e)}")
        
        # ⭐ DETERMINAR TAMAÑO DE LA IMAGEN FINAL (con validación)
        alto, ancho = None, None
        
        if mask_nucleo is not None and len(mask_nucleo.shape) == 2:
            alto, ancho = mask_nucleo.shape
            print(f"📐 Usando dimensiones de núcleo: {ancho}x{alto}")
        elif mask_micronucleo is not None and len(mask_micronucleo.shape) == 2:
            alto, ancho = mask_micronucleo.shape
            print(f"📐 Usando dimensiones de micronúcleo: {ancho}x{alto}")
        elif mask_membrana is not None and len(mask_membrana.shape) == 2:
            alto, ancho = mask_membrana.shape
            print(f"📐 Usando dimensiones de membrana: {ancho}x{alto}")
        else:
            print("❌ ERROR: No hay máscaras válidas disponibles")
            print(f"   mask_nucleo: {mask_nucleo.shape if mask_nucleo is not None else 'None'}")
            print(f"   mask_micronucleo: {mask_micronucleo.shape if mask_micronucleo is not None else 'None'}")
            print(f"   mask_membrana: {mask_membrana.shape if mask_membrana is not None else 'None'}")
            return HttpResponse("No hay máscaras válidas disponibles", status=404)
        
        print(f"🎨 Creando imagen overlay de {ancho}x{alto}...")
        
        # Crear imagen RGBA (transparente)
        img = Image.new('RGBA', (ancho, alto), (0, 0, 0, 0))
        pixels = img.load()
        
        # Aplicar colores capa por capa
        print("🎨 Aplicando colores...")
        for y in range(alto):
            for x in range(ancho):
                # Membrana primero (más transparente, capa de fondo)
                if mask_membrana is not None and len(mask_membrana.shape) == 2 and mask_membrana[y, x] > 0:
                    pixels[x, y] = (0, 120, 255, 160)  # Azul claro
                
                # Núcleo (capa intermedia)
                if mask_nucleo is not None and len(mask_nucleo.shape) == 2 and mask_nucleo[y, x] > 0:
                    pixels[x, y] = (0, 255, 0, 220)  # Verde
                
                # Micronúcleo (más opaco, capa superior para destacar)
                if mask_micronucleo is not None and len(mask_micronucleo.shape) == 2 and mask_micronucleo[y, x] > 0:
                    pixels[x, y] = (255, 0, 0, 255)  # Rojo brillante
        
        print("✅ Overlay creado, generando PNG...")
        
        # Convertir a bytes
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        print(f"✅ PNG generado: {len(buffer.getvalue())} bytes")
        
        return HttpResponse(buffer.getvalue(), content_type='image/png')
        
    except Exception as e:   
        print(f"❌ ERROR INESPERADO: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return HttpResponse(f"Error generando overlay: {str(e)}", status=500)