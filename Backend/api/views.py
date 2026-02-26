# -*- coding: utf-8 -*-
import os
import io
import threading
import requests
import numpy as np

from django.utils import timezone
from django.http import HttpResponse
from django.db import transaction
from django.db.models import F

from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from PIL import Image

from .models import (
    Paciente, CasoClinico, Muestra, Analisis,
    AnalisisResultados, AnalisisArchivos, AnalisisJob
)
from .serializers import (
    PacienteSerializer, CasoClinicoSerializer, MuestraSerializer,
    AnalisisSerializer, AnalisisArchivosSerializer, AnalisisJobSerializer
)

FASTAPI_URL = "http://127.0.0.1:8001"


# ============================================================================
# VIEWSETS
# ============================================================================

class PacienteViewSet(viewsets.ModelViewSet):
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer

    @action(detail=True, methods=['get'])
    def casos(self, request, pk=None):
        paciente = self.get_object()
        casos = paciente.casos.all()
        serializer = CasoClinicoSerializer(casos, many=True)
        return Response(serializer.data)


class CasoClinicoViewSet(viewsets.ModelViewSet):
    queryset = CasoClinico.objects.all()
    serializer_class = CasoClinicoSerializer

    @action(detail=True, methods=['get'])
    def analisis(self, request, pk=None):
        caso = self.get_object()
        analisis = Analisis.objects.filter(id_muestra_fk__id_caso_fk=caso)
        serializer = AnalisisSerializer(analisis, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def muestras(self, request, pk=None):
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
        analisis = self.get_object()
        nuevo_estado = request.data.get('estado')
        estados_validos = ['pendiente', 'proceso', 'listo', 'error']
        if nuevo_estado in estados_validos:
            analisis.estado = nuevo_estado
            analisis.save()
            return Response({'status': 'Estado actualizado'})
        return Response({'error': 'Estado no valido'}, status=status.HTTP_400_BAD_REQUEST)


class MuestraCreateView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        serializer = MuestraSerializer(data=request.data)
        if serializer.is_valid():
            muestra = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============================================================================
# MASCARAS - dibuja poligonos desde contornos (formato FastAPI)
# {"objetos": [{"tipo": "membrana"|"nucleo"|"micronucleo", "puntos": [[x,y],...]}]}
# ============================================================================

from PIL import ImageDraw

_COLORES_RGBA = {
    'membrana':    (0,   120, 255, 140),
    'nucleo':      (0,   220,   0, 200),
    'micronucleo': (255,   0,   0, 230),
}
# Orden de dibujo: membrana primero (fondo), micronucleo encima (prioridad)
_ORDEN_OVERLAY = ['membrana', 'nucleo', 'micronucleo']


def _dibujar_mascaras(objetos, ancho, alto, tipos_a_mostrar):
    """
    Dibuja los poligonos de los tipos indicados sobre un canvas RGBA.
    objetos: lista de {"tipo": str, "puntos": [[x,y], ...]}
    tipos_a_mostrar: lista de tipos a incluir, ej ['nucleo', 'micronucleo']
    """
    canvas = Image.new('RGBA', (ancho, alto), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    for tipo in _ORDEN_OVERLAY:
        if tipo not in tipos_a_mostrar:
            continue
        color = _COLORES_RGBA[tipo]
        for obj in objetos:
            if obj.get('tipo') != tipo:
                continue
            puntos = obj.get('puntos', [])
            if len(puntos) < 3:
                continue
            poligono = [tuple(p) for p in puntos]
            draw.polygon(poligono, fill=color)

    return canvas


def _canvas_a_png(img):
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf.getvalue()


@api_view(['GET'])
def obtener_mascara_png(request, id_analisis, tipo_mascara):
    """
    GET /api/mascaras/{id_analisis}/{tipo_mascara}/
    tipo_mascara: nucleo | micronucleo | membrana | overlay
    """
    tipos_validos = list(_COLORES_RGBA.keys()) + ['overlay']
    if tipo_mascara not in tipos_validos:
        return HttpResponse(f"Tipo invalido. Usa: {', '.join(tipos_validos)}", status=400)

    try:
        analisis = Analisis.objects.select_related('id_muestra_fk').get(id_analisis=id_analisis)
        archivo  = AnalisisArchivos.objects.get(id_analisis_fk=analisis, activo=True)
        objetos  = archivo.contenido_json.get('objetos', [])

        if not objetos:
            return HttpResponse("No hay objetos en el JSON de este analisis", status=404)

        # Obtener dimensiones reales de la imagen original
        muestra = analisis.id_muestra_fk
        with Image.open(muestra.ruta_imagen.path) as img_original:
            ancho, alto = img_original.size

        # Determinar que tipos dibujar
        if tipo_mascara == 'overlay':
            tipos_a_mostrar = _ORDEN_OVERLAY
        else:
            tipos_a_mostrar = [tipo_mascara]

        canvas = _dibujar_mascaras(objetos, ancho, alto, tipos_a_mostrar)

        # Verificar que se dibujo algo
        import numpy as np
        arr = np.array(canvas)
        if arr[:, :, 3].max() == 0:
            return HttpResponse(f"No hay objetos de tipo '{tipo_mascara}' en este analisis", status=404)

        resp = HttpResponse(_canvas_a_png(canvas), content_type='image/png')
        resp['Cache-Control'] = 'private, max-age=60'
        return resp

    except Analisis.DoesNotExist:
        return HttpResponse("Analisis no encontrado", status=404)
    except AnalisisArchivos.DoesNotExist:
        return HttpResponse("No hay version activa para este analisis", status=404)
    except Exception as e:
        return HttpResponse(f"Error generando mascara: {e}", status=500)


@api_view(['GET'])
def obtener_json_activo(request, id_analisis):
    try:
        archivo = AnalisisArchivos.objects.get(id_analisis_fk=id_analisis, activo=True)
    except AnalisisArchivos.DoesNotExist:
        return Response({"detail": "No existe JSON activo"}, status=status.HTTP_404_NOT_FOUND)
    return Response(AnalisisArchivosSerializer(archivo).data)


@api_view(['PATCH'])
def guardar_edicion(request, id_analisis):
    """
    PATCH /api/analisis/{id}/editar/
    Guarda edicion manual. Crea nueva version (max 3).
    Nunca elimina la version original del modelo (es_resultado_modelo=True).
    Body: { "objetos": [{"tipo": "membrana"|"nucleo"|"micronucleo", "puntos": [[x,y],...]}] }
    """
    try:
        analisis = Analisis.objects.get(id_analisis=id_analisis)
    except Analisis.DoesNotExist:
        return Response({"error": "Analisis no encontrado"}, status=404)

    objetos = request.data.get('objetos')
    if objetos is None:
        return Response({"error": "Se requiere el campo 'objetos'"}, status=400)

    MAX_VERSIONES = 3

    with transaction.atomic():
        versiones = list(
            AnalisisArchivos.objects.filter(id_analisis_fk=analisis).order_by('version')
        )

        # Si ya hay MAX_VERSIONES, eliminar la edicion manual mas antigua
        # (nunca la version del modelo original)
        if len(versiones) >= MAX_VERSIONES:
            a_eliminar = next((v for v in versiones if not v.es_resultado_modelo), None)
            if a_eliminar:
                a_eliminar.delete()

        # Recalcular conteos desde los objetos editados
        nucleos      = sum(1 for o in objetos if o.get('tipo') == 'nucleo')
        micronucleos = sum(1 for o in objetos if o.get('tipo') == 'micronucleo')
        membranas    = sum(1 for o in objetos if o.get('tipo') == 'membrana')

        # Crear nueva version — el save() del modelo auto-incrementa version
        # y desactiva la anterior gracias a la logica en AnalisisArchivos.save()
        nuevo = AnalisisArchivos.objects.create(
            id_analisis_fk=analisis,
            contenido_json={'objetos': objetos},
            es_resultado_modelo=False,
            activo=True,
        )

        # Actualizar conteos en AnalisisResultados
        AnalisisResultados.objects.update_or_create(
            id_analisis_fk=analisis,
            defaults={
                'total_nucleos':      nucleos,
                'total_micronucleos': micronucleos,
                'total_membranas':    membranas,
            }
        )

    versiones_totales = AnalisisArchivos.objects.filter(id_analisis_fk=analisis).count()
    return Response({
        'version':           nuevo.version,
        'versiones_totales': versiones_totales,
        'max_versiones':     MAX_VERSIONES,
        'nucleos':           nucleos,
        'micronucleos':      micronucleos,
        'membranas':         membranas,
    }, status=201)



def worker_analizar_caso(job_id):
    from django.db import connection as db_connection
    db_connection.close()

    try:
        job = AnalisisJob.objects.get(id_job=job_id)
        caso = job.id_caso_fk
        todas = Muestra.objects.filter(id_caso_fk=caso)

        if job.es_reproceso:
            muestras_a_procesar = list(todas)
        else:
            ids_con_analisis = Analisis.objects.filter(
                id_muestra_fk__id_caso_fk=caso,
                estado='listo'
            ).values_list('id_muestra_fk_id', flat=True)
            muestras_a_procesar = list(todas.exclude(id_muestra__in=ids_con_analisis))

        AnalisisJob.objects.filter(id_job=job_id).update(
            estado='en_proceso',
            total_imagenes=len(muestras_a_procesar),
        )

        for muestra in muestras_a_procesar:
            try:
                with open(muestra.ruta_imagen.path, 'rb') as img_file:
                    respuesta = requests.post(
                        f"{FASTAPI_URL}/segmentar",
                        files={"file": (os.path.basename(muestra.ruta_imagen.name), img_file, "image/png")},
                        timeout=120
                    )
                    respuesta.raise_for_status()
                    resultado_json = respuesta.json()

                with transaction.atomic():
                    analisis, creado = Analisis.objects.get_or_create(
                        id_muestra_fk=muestra,
                        defaults={'version_modelo': job.version_modelo, 'estado': 'proceso'}
                    )
                    if not creado:
                        analisis.estado = 'proceso'
                        analisis.save(update_fields=['estado'])

                    AnalisisArchivos.objects.create(
                        id_analisis_fk=analisis,
                        contenido_json=resultado_json,
                        es_resultado_modelo=True,
                        activo=True,
                    )

                    objetos      = resultado_json.get('objetos', [])
                    nucleos      = sum(1 for o in objetos if o.get('tipo') == 'nucleo')
                    micronucleos = sum(1 for o in objetos if o.get('tipo') == 'micronucleo')
                    membranas    = sum(1 for o in objetos if o.get('tipo') == 'membrana')

                    AnalisisResultados.objects.update_or_create(
                        id_analisis_fk=analisis,
                        defaults={
                            'total_nucleos': nucleos,
                            'total_micronucleos': micronucleos,
                            'total_membranas': membranas,
                        }
                    )
                    analisis.estado = 'listo'
                    analisis.save(update_fields=['estado'])

                AnalisisJob.objects.filter(id_job=job_id).update(procesadas=F('procesadas') + 1)
                print(f"[Job {job_id}] Muestra {muestra.id_muestra} procesada")

            except Exception as e:
                print(f"[Job {job_id}] Error muestra {muestra.id_muestra}: {e}")
                AnalisisJob.objects.filter(id_job=job_id).update(
                    procesadas=F('procesadas') + 1,
                    errores=F('errores') + 1,
                )

        job.refresh_from_db()
        estado_final = 'completado' if job.errores == 0 else 'error'
        AnalisisJob.objects.filter(id_job=job_id).update(estado=estado_final, fecha_fin=timezone.now())
        print(f"[Job {job_id}] {estado_final}")

    except Exception as e:
        print(f"[Job {job_id}] Error fatal: {e}")
        try:
            AnalisisJob.objects.filter(id_job=job_id).update(
                estado='error', mensaje_error=str(e), fecha_fin=timezone.now()
            )
        except Exception:
            pass


# ============================================================================
# ENDPOINTS JOB
# ============================================================================

@api_view(['POST'])
def iniciar_analisis(request, id_caso):
    try:
        caso = CasoClinico.objects.get(id_caso=id_caso)
    except CasoClinico.DoesNotExist:
        return Response({"error": "Caso no encontrado"}, status=404)

    job_activo = AnalisisJob.objects.filter(
        id_caso_fk=caso, estado__in=['pendiente', 'en_proceso']
    ).first()

    if job_activo:
        return Response({
            "error": "Ya hay un analisis en progreso",
            "job_id": job_activo.id_job,
            "progreso": job_activo.progreso_porcentaje,
            "estado": job_activo.estado,
        }, status=409)

    total = Muestra.objects.filter(id_caso_fk=caso).count()
    if total == 0:
        return Response({"error": "Este caso no tiene muestras"}, status=400)

    ids_con_analisis = Analisis.objects.filter(
        id_muestra_fk__id_caso_fk=caso, estado='listo'
    ).values_list('id_muestra_fk_id', flat=True)

    sin_analizar = total - len(ids_con_analisis)
    es_reproceso = sin_analizar == 0

    job = AnalisisJob.objects.create(
        id_caso_fk=caso,
        estado='pendiente',
        es_reproceso=es_reproceso,
        version_modelo=request.data.get('version_modelo', 'cellpose-v1'),
    )

    threading.Thread(
        target=worker_analizar_caso,
        args=(job.id_job,),
        daemon=True,
        name=f"worker-job-{job.id_job}"
    ).start()

    return Response({
        "job_id": job.id_job,
        "es_reproceso": es_reproceso,
        "estado": "pendiente",
        "sin_analizar": sin_analizar,
        "total": total,
        "mensaje": "Analisis iniciado. Puede seguir navegando.",
    }, status=202)


@api_view(['GET'])
def estado_job(request, job_id):
    try:
        job = AnalisisJob.objects.get(id_job=job_id)
    except AnalisisJob.DoesNotExist:
        return Response({"error": "Job no encontrado"}, status=404)
    return Response(AnalisisJobSerializer(job).data)


@api_view(['GET'])
def job_activo_caso(request, id_caso):
    job_en_curso = AnalisisJob.objects.filter(
        id_caso_fk=id_caso, estado__in=['pendiente', 'en_proceso']
    ).first()

    if job_en_curso:
        return Response({"hay_job_activo": True, "job": AnalisisJobSerializer(job_en_curso).data})

    ultimo_job = AnalisisJob.objects.filter(id_caso_fk=id_caso).order_by('-fecha_inicio').first()
    total = Muestra.objects.filter(id_caso_fk=id_caso).count()
    ids_con_analisis = Analisis.objects.filter(
        id_muestra_fk__id_caso_fk=id_caso, estado='listo'
    ).values_list('id_muestra_fk_id', flat=True)
    sin_analizar = total - len(ids_con_analisis)

    return Response({
        "hay_job_activo": False,
        "sin_analizar": sin_analizar,
        "total_muestras": total,
        "es_reproceso": sin_analizar == 0 and total > 0,
        "job": AnalisisJobSerializer(ultimo_job).data if ultimo_job else None,
    })