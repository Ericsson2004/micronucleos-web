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


# ============================================================================
# CARACTERIZACIÓN MORFOMÉTRICA  +  PARÁMETROS MoA  (Huang et al., 2017)
#
# Implementa los 6 parámetros del paper para clasificación futura
# aneugen / clastogen mediante Bayesian k-means:
#
#   Parámetro       Definición (paper)
#   ─────────────── ────────────────────────────────────────────────────────
#   area            Área del micronúcleo  (px²)
#   fra_area        Área MN / Área núcleo  (fracción adimensional)
#   roundness       4π·A / P²  (1.0 = círculo perfecto)  ← misma que circularity
#   compactness     Área del disco inscrito máximo / Área total del MN
#   distance        Distancia mínima borde-a-borde MN ↔ núcleo más cercano (px)
#   fra_intensity   Intensidad media MN / Intensidad media núcleo  (requiere imagen → None por ahora)
#
# La combinación Distance + Compactness + Roundness obtuvo 93.39 % de
# precisión en el paper.  Estos valores se devuelven por cada MN para que
# el clasificador Bayesian k-means pueda usarlos directamente en el futuro.
#
# GET /api/casos/{id_caso}/caracterizacion/
# ============================================================================

# ── helpers geométricos ──────────────────────────────────────────────────────

def _poligono_area(pts):
    """Shoelace — área con signo positivo."""
    x, y = pts[:, 0], pts[:, 1]
    return abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1))) / 2.0


def _poligono_perimetro(pts):
    diffs = np.diff(pts, axis=0, append=pts[:1])
    return float(np.sum(np.linalg.norm(diffs, axis=1)))


def _centroide(pts):
    return float(np.mean(pts[:, 0])), float(np.mean(pts[:, 1]))


def _distancia_euclidea(c1, c2):
    return ((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2) ** 0.5


def _distancia_minima_bordes(pts_a, pts_b):
    """
    Distancia mínima borde-a-borde entre dos polígonos.
    Calcula la distancia mínima entre todos los pares de vértices.
    Aproximación eficiente sin necesidad de scipy.
    """
    min_d = np.inf
    for va in pts_a:
        dists = np.linalg.norm(pts_b - va, axis=1)
        d = dists.min()
        if d < min_d:
            min_d = d
    return round(float(min_d), 3)


def _compactness(pts, area):
    """
    Compactness = área del disco inscrito máximo / área del polígono.
    El radio del disco inscrito máximo se estima como la distancia
    mínima del centroide a cualquier vértice del borde (radio inscrito
    aproximado conservador), siguiendo la definición del paper.
    """
    cx, cy  = _centroide(pts)
    radios  = np.linalg.norm(pts - np.array([cx, cy]), axis=1)
    r_insc  = float(radios.min())           # radio conservador del disco inscrito
    area_disco = np.pi * r_insc ** 2
    if area > 0:
        return round(min(area_disco / area, 1.0), 4)
    return 0.0


def _metricas_completas(puntos):
    """
    Calcula todas las métricas geométricas de un polígono:
      area, perimeter, roundness (=circularity), compactness,
      major_axis, minor_axis, centroid
    """
    pts = np.array(puntos, dtype=np.float64)
    if len(pts) < 3:
        return None

    area      = _poligono_area(pts)
    perimeter = _poligono_perimetro(pts)
    cx, cy    = _centroide(pts)

    # Roundness  =  4π·A / P²   (Paper: Table 2 — "Roundness of MN morphology")
    roundness = round(min((4 * np.pi * area) / (perimeter ** 2), 1.0), 4) if perimeter > 0 else 0.0

    # Ejes mayor / menor via eigenvalores de covarianza
    centered  = pts - np.array([cx, cy])
    cov       = np.cov(centered.T)
    if cov.ndim == 2:
        eigvals, _ = np.linalg.eigh(cov)
        eigvals    = np.sort(np.abs(eigvals))[::-1]
        major_axis = round(4 * np.sqrt(eigvals[0]) if eigvals[0] > 0 else 0, 2)
        minor_axis = round(4 * np.sqrt(eigvals[1]) if eigvals[1] > 0 else 0, 2)
    else:
        major_axis = minor_axis = 0.0

    comp = _compactness(pts, area)

    return {
        'area':        round(float(area), 3),
        'perimeter':   round(float(perimeter), 3),
        'roundness':   roundness,       # = circularity  (4πA/P²)
        'compactness': comp,            # área disco inscrito / área total
        'major_axis':  major_axis,
        'minor_axis':  minor_axis,
        'centroid':    (cx, cy),
        '_pts':        pts,             # referencia interna para distancias
    }


def _metricas_mn_moa(mn_met, nucleo_met):
    """
    Calcula los parámetros MoA específicos del paper para un micronúcleo
    dado su núcleo asociado.

    Parámetros devueltos:
      roundness    : ya calculado en _metricas_completas
      compactness  : ya calculado en _metricas_completas
      area         : área del MN en px²
      fra_area     : área MN / área núcleo  (fracción adimensional)
      distance     : distancia mínima borde MN ↔ borde núcleo (px)
      fra_intensity: None hasta que se implemente lectura de imagen
    """
    fra_area = round(mn_met['area'] / nucleo_met['area'], 4) if nucleo_met['area'] > 0 else None

    distance = _distancia_minima_bordes(mn_met['_pts'], nucleo_met['_pts'])

    return {
        'area':          mn_met['area'],
        'roundness':     mn_met['roundness'],
        'compactness':   mn_met['compactness'],
        'fra_area':      fra_area,
        'distance':      distance,
        # Huang et al.: ratio intensidad media MN / intensidad media núcleo
        # Requiere acceso a píxeles de la imagen original → implementación futura
        'fra_intensity': None,
    }


def _caracterizar_muestra(objetos, id_muestra, idx_base):
    """
    Procesa el array de objetos de un JSON de análisis y calcula:
      - Métricas morfométricas de cada MEMBRANA (tabla principal)
      - Parámetros MoA de cada MICRONÚCLEO (Huang et al., 2017)

    Asociaciones:
      - Cada MN → núcleo más cercano por centroide (para fra_area, distance)
      - Cada MN → membrana más cercana por centroide (para conteo por célula)

    Returns: lista de dicts por membrana, cada uno con la lista de sus MNs
             y sus parámetros MoA individuales.
    """
    membranas    = [o for o in objetos if o.get('tipo') == 'membrana']
    nucleos      = [o for o in objetos if o.get('tipo') == 'nucleo']
    micronucleos = [o for o in objetos if o.get('tipo') == 'micronucleo']

    # ── Calcular métricas de membranas ───────────────────────────────────
    mem_met = []
    for m in membranas:
        met = _metricas_completas(m.get('puntos', []))
        if met:
            mem_met.append(met)

    if not mem_met:
        return []

    # ── Calcular métricas de núcleos ─────────────────────────────────────
    nuc_met = []
    for n in nucleos:
        met = _metricas_completas(n.get('puntos', []))
        if met:
            nuc_met.append(met)

    # ── Calcular métricas completas de cada micronúcleo ──────────────────
    mn_met_list = []
    for mn in micronucleos:
        met = _metricas_completas(mn.get('puntos', []))
        if met:
            mn_met_list.append(met)

    # ── Asociar cada MN → núcleo más cercano (centroide) ─────────────────
    # Necesario para fra_area y distance (paper: distancia borde-a-borde MN ↔ núcleo)
    mn_moa_params = []
    for mn_m in mn_met_list:
        if nuc_met:
            dists_nuc  = [_distancia_euclidea(mn_m['centroid'], n['centroid']) for n in nuc_met]
            nucleo_mas_cercano = nuc_met[int(np.argmin(dists_nuc))]
        else:
            # Sin núcleo detectado: fra_area y distance quedan None
            nucleo_mas_cercano = {'area': 0, '_pts': mn_m['_pts']}

        moa = _metricas_mn_moa(mn_m, nucleo_mas_cercano)
        moa['centroid'] = mn_m['centroid']   # guardamos para asociar a membrana
        mn_moa_params.append(moa)

    # ── Asociar cada MN → membrana más cercana (conteo por célula) ───────
    mn_por_membrana = [[] for _ in mem_met]
    for moa in mn_moa_params:
        dists_mem = [_distancia_euclidea(moa['centroid'], m['centroid']) for m in mem_met]
        idx_min   = int(np.argmin(dists_mem))
        mn_por_membrana[idx_min].append(moa)

    # ── Construir resultado final por membrana ───────────────────────────
    resultados = []
    for i, met in enumerate(mem_met):
        mns         = mn_por_membrana[i]
        mn_count    = len(mns)
        mn_area_tot = round(sum(mn['area'] for mn in mns), 3)

        # Parámetros MoA limpios por MN (sin centroid interno)
        mns_serializables = [
            {
                'area':          mn['area'],
                'roundness':     mn['roundness'],
                'compactness':   mn['compactness'],
                'fra_area':      mn['fra_area'],
                'distance':      mn['distance'],
                'fra_intensity': mn['fra_intensity'],
            }
            for mn in mns
        ]

        resultados.append({
            # ── Identificación ──────────────────────────────────────────
            'id_membrana': idx_base + i + 1,
            'id_muestra':  id_muestra,

            # ── Métricas de la membrana (tabla principal del front) ──────
            'size':        met['area'],           # área membrana (px²)
            'circularity': met['roundness'],       # 4πA/P² de la membrana
            'major_axis':  met['major_axis'],
            'minor_axis':  met['minor_axis'],
            'perimeter':   met['perimeter'],

            # ── Conteo de MN ─────────────────────────────────────────────
            'mn_count':    mn_count,
            'mn_area':     mn_area_tot,            # suma áreas de sus MN

            # ── Parámetros MoA por MN (Huang et al., 2017) ───────────────
            # Listos para alimentar el clasificador Bayesian k-means futuro.
            # Combinación óptima del paper: distance + compactness + roundness
            # → 93.39 % de precisión aneugen/clastogen.
            'micronucleos_moa': mns_serializables,

            # ── Intensidad (requiere imagen original → fase futura) ───────
            'intensity': None,
        })

    return resultados


@api_view(['GET'])
def caracterizar_caso(request, id_caso):
    """
    GET /api/casos/{id_caso}/caracterizacion/

    Recorre todas las muestras del caso con análisis en estado 'listo',
    obtiene el JSON activo de cada una y calcula:
      - Métricas morfométricas por membrana  (tabla del frontend)
      - Parámetros MoA por micronúcleo       (Huang et al., 2017)

    Response 200:
    {
        "total_membranas":           N,
        "total_muestras_analizadas": M,
        "membranas": [
            {
                "id_membrana":   1,
                "id_muestra":    5,
                "size":          312.5,       # área membrana px²
                "circularity":   0.87,        # 4πA/P² membrana
                "major_axis":    22.1,
                "minor_axis":    15.3,
                "perimeter":     67.4,
                "mn_count":      2,
                "mn_area":       18.3,        # suma áreas MN px²
                "intensity":     null,        # pendiente imagen
                "micronucleos_moa": [
                    {
                        "area":          9.1,
                        "roundness":     0.82,   # paper: Roundness
                        "compactness":   0.61,   # paper: Compactness
                        "fra_area":      0.029,  # paper: Fra area (MN/núcleo)
                        "distance":      3.2,    # paper: Distance borde-a-borde (px)
                        "fra_intensity": null    # paper: Fra intensity → pendiente
                    }, ...
                ]
            }, ...
        ]
    }

    Response 202: segmentación aún en progreso.
    Response 404: caso no existe o sin muestras analizadas.
    """
    try:
        caso = CasoClinico.objects.get(id_caso=id_caso)
    except CasoClinico.DoesNotExist:
        return Response({"error": "Caso no encontrado"}, status=404)

    # Bloquear si la segmentación está corriendo
    job_activo = AnalisisJob.objects.filter(
        id_caso_fk=caso, estado__in=['pendiente', 'en_proceso']
    ).first()
    if job_activo:
        return Response({
            "error":    "La segmentación está en progreso, espera a que finalice.",
            "progreso": job_activo.progreso_porcentaje,
            "estado":   job_activo.estado,
        }, status=202)

    analisis_listos = Analisis.objects.filter(
        id_muestra_fk__id_caso_fk=caso,
        estado='listo'
    ).select_related('id_muestra_fk').prefetch_related('archivos')

    if not analisis_listos.exists():
        return Response({
            "error": "Este caso no tiene muestras analizadas. Ejecuta la segmentación primero."
        }, status=404)

    todas_membranas = []
    idx_base        = 0
    muestras_ok     = 0

    for analisis in analisis_listos:
        archivo = analisis.archivos.filter(activo=True).first()
        if not archivo:
            continue

        objetos   = archivo.contenido_json.get('objetos', [])
        id_mues   = analisis.id_muestra_fk.id_muestra
        resultado = _caracterizar_muestra(objetos, id_mues, idx_base)

        if resultado:
            todas_membranas.extend(resultado)
            idx_base    += len(resultado)
            muestras_ok += 1

    if not todas_membranas:
        return Response({
            "error": "Los análisis no contienen membranas detectadas."
        }, status=404)

    return Response({
        "total_membranas":           len(todas_membranas),
        "total_muestras_analizadas": muestras_ok,
        "membranas":                 todas_membranas,
    })