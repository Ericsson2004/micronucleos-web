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
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny

from rest_framework_simplejwt.tokens import RefreshToken

from PIL import Image
from PIL import ImageDraw, ImageFont

from .models import (
    Doctor,
    Paciente, CasoClinico, Muestra, Analisis,
    AnalisisResultados, AnalisisArchivos, AnalisisJob
)
from .serializers import (
    LoginSerializer,
    DoctorSerializer, DoctorCreateSerializer, DoctorUpdateSerializer,
    PacienteSerializer, CasoClinicoSerializer, MuestraSerializer,
    AnalisisSerializer, AnalisisArchivosSerializer, AnalisisJobSerializer
)

FASTAPI_URL = "http://127.0.0.1:8001"


# ============================================================================
# AUTH — Login / Logout / Me
# ============================================================================

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    POST /api/auth/login/
    Body: { "email": "...", "password": "..." }
    Response: { "access": "...", "refresh": "...", "doctor": {...} }
    """
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user   = serializer.validated_data['user']
    doctor = user.doctor

    refresh = RefreshToken.for_user(user)

    return Response({
        'access':  str(refresh.access_token),
        'refresh': str(refresh),
        'doctor':  DoctorSerializer(doctor).data,
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    POST /api/auth/logout/
    Body: { "refresh": "..." }
    Blacklistea el refresh token.
    """
    try:
        refresh_token = request.data.get('refresh')
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'detail': 'Sesión cerrada correctamente.'}, status=status.HTTP_200_OK)
    except Exception:
        return Response({'detail': 'Token inválido o ya expirado.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    """
    GET /api/auth/me/
    Devuelve el perfil del doctor autenticado.
    """
    try:
        doctor = request.user.doctor
    except Doctor.DoesNotExist:
        return Response({'error': 'Sin perfil de doctor.'}, status=status.HTTP_403_FORBIDDEN)

    return Response(DoctorSerializer(doctor).data)


# ============================================================================
# CRUD DOCTORES — solo admin (is_staff)
# ============================================================================

class DoctorViewSet(viewsets.ViewSet):
    """
    CRUD completo de doctores.
    Solo accesible por usuarios con is_staff=True (administrador).
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    def list(self, request):
        """GET /api/doctores/ — lista todos los doctores"""
        doctores = Doctor.objects.select_related('user').all().order_by('apellido')
        serializer = DoctorSerializer(doctores, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """GET /api/doctores/{id}/"""
        try:
            doctor = Doctor.objects.select_related('user').get(pk=pk)
        except Doctor.DoesNotExist:
            return Response({'error': 'Doctor no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(DoctorSerializer(doctor).data)

    def create(self, request):
        """POST /api/doctores/ — crea usuario + perfil doctor"""
        serializer = DoctorCreateSerializer(data=request.data)
        if serializer.is_valid():
            doctor = serializer.save()
            return Response(DoctorSerializer(doctor).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        """PATCH /api/doctores/{id}/"""
        try:
            doctor = Doctor.objects.get(pk=pk)
        except Doctor.DoesNotExist:
            return Response({'error': 'Doctor no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = DoctorUpdateSerializer(doctor, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(DoctorSerializer(doctor).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """DELETE /api/doctores/{id}/ — desactiva en lugar de borrar"""
        try:
            doctor = Doctor.objects.get(pk=pk)
        except Doctor.DoesNotExist:
            return Response({'error': 'Doctor no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        # Soft delete: desactivar en lugar de eliminar físicamente
        doctor.activo = False
        doctor.user.is_active = False
        doctor.user.save(update_fields=['is_active'])
        doctor.save(update_fields=['activo'])
        return Response({'detail': 'Doctor desactivado.'}, status=status.HTTP_200_OK)


# ============================================================================
# VIEWSETS — filtrados por doctor autenticado
# ============================================================================

class PacienteViewSet(viewsets.ModelViewSet):
    serializer_class = PacienteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Cada doctor solo ve sus propios pacientes
        try:
            doctor = self.request.user.doctor
            return Paciente.objects.filter(id_doctor_fk=doctor)
        except Doctor.DoesNotExist:
            return Paciente.objects.none()

    def perform_create(self, serializer):
        # Al crear paciente, se asigna automáticamente al doctor logueado
        doctor = self.request.user.doctor
        serializer.save(id_doctor_fk=doctor)

    @action(detail=True, methods=['get'])
    def casos(self, request, pk=None):
        paciente = self.get_object()
        casos = paciente.casos.all()
        serializer = CasoClinicoSerializer(casos, many=True)
        return Response(serializer.data)


class CasoClinicoViewSet(viewsets.ModelViewSet):
    serializer_class = CasoClinicoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Solo casos de pacientes del doctor logueado
        try:
            doctor = self.request.user.doctor
            return CasoClinico.objects.filter(id_paciente_fk__id_doctor_fk=doctor)
        except Doctor.DoesNotExist:
            return CasoClinico.objects.none()

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
    serializer_class = MuestraSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        try:
            doctor = self.request.user.doctor
            return Muestra.objects.filter(id_caso_fk__id_paciente_fk__id_doctor_fk=doctor)
        except Doctor.DoesNotExist:
            return Muestra.objects.none()


class AnalisisViewSet(viewsets.ModelViewSet):
    serializer_class = AnalisisSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        try:
            doctor = self.request.user.doctor
            return Analisis.objects.filter(
                id_muestra_fk__id_caso_fk__id_paciente_fk__id_doctor_fk=doctor
            )
        except Doctor.DoesNotExist:
            return Analisis.objects.none()

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
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = MuestraSerializer(data=request.data)
        if serializer.is_valid():
            muestra = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============================================================================
# MÁSCARAS
# ============================================================================

from PIL import ImageDraw

_COLORES_RGBA = {
    'membrana':    (0,   120, 255, 140),
    'nucleo':      (0,   220,   0, 200),
    'micronucleo': (255,   0,   0, 230),
}
_ORDEN_OVERLAY = ['membrana', 'nucleo', 'micronucleo']


def _dibujar_mascaras(objetos, ancho, alto, tipos_a_mostrar, dibujar_numeros=False, offset=0):
    canvas = Image.new('RGBA', (ancho, alto), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    font = None
    if dibujar_numeros:
        tamaño_letra = 70
        try:
            font = ImageFont.truetype("arial.ttf", tamaño_letra)
        except IOError:
            try:
                font = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", tamaño_letra)
            except IOError:
                font = ImageFont.load_default()

    textos_a_dibujar = []

    for tipo in _ORDEN_OVERLAY:
        if tipo not in tipos_a_mostrar:
            continue
        color = _COLORES_RGBA[tipo]
        objetos_filtrados = [obj for obj in objetos if obj.get('tipo') == tipo]
        for i, obj in enumerate(objetos_filtrados):
            puntos = obj.get('puntos', [])
            if len(puntos) < 3:
                continue
            poligono = [tuple(p) for p in puntos]
            draw.polygon(poligono, fill=color)
            if tipo == 'membrana' and dibujar_numeros:
                pts_array = np.array(puntos)
                cx = int(np.mean(pts_array[:, 0]))
                cy = int(np.mean(pts_array[:, 1]))
                textos_a_dibujar.append((cx, cy, f"#{offset + i + 1}"))

    for cx, cy, text in textos_a_dibujar:
        grosor_borde = 2
        for dx in range(-grosor_borde, grosor_borde + 1):
            for dy in range(-grosor_borde, grosor_borde + 1):
                if dx != 0 or dy != 0:
                    draw.text((cx + dx, cy + dy), text, font=font, fill=(0, 0, 0, 255))
        draw.text((cx, cy), text, font=font, fill=(255, 255, 255, 255))

    return canvas


def _canvas_a_png(img):
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf.getvalue()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_mascara_png(request, id_analisis, tipo_mascara):
    tipos_validos = list(_COLORES_RGBA.keys()) + ['overlay']
    if tipo_mascara not in tipos_validos:
        return HttpResponse(f"Tipo invalido. Usa: {', '.join(tipos_validos)}", status=400)

    try:
        analisis = Analisis.objects.select_related('id_muestra_fk').get(id_analisis=id_analisis)
        archivo  = AnalisisArchivos.objects.get(id_analisis_fk=analisis, activo=True)
        objetos  = archivo.contenido_json.get('objetos', [])

        if not objetos:
            return HttpResponse("No hay objetos en el JSON de este analisis", status=404)

        muestra = analisis.id_muestra_fk
        with Image.open(muestra.ruta_imagen.path) as img_original:
            ancho, alto = img_original.size

        if tipo_mascara == 'overlay':
            tipos_a_mostrar = _ORDEN_OVERLAY
        else:
            tipos_a_mostrar = [tipo_mascara]

        offset_param = request.GET.get('offset')
        dibujar_numeros = offset_param is not None
        offset_val = int(offset_param) if dibujar_numeros else 0

        canvas = _dibujar_mascaras(objetos, ancho, alto, tipos_a_mostrar, dibujar_numeros, offset_val)

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
@permission_classes([IsAuthenticated])
def obtener_json_activo(request, id_analisis):
    try:
        archivo = AnalisisArchivos.objects.get(id_analisis_fk=id_analisis, activo=True)
    except AnalisisArchivos.DoesNotExist:
        return Response({"detail": "No existe JSON activo"}, status=status.HTTP_404_NOT_FOUND)
    return Response(AnalisisArchivosSerializer(archivo).data)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def guardar_edicion(request, id_analisis):
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
        if len(versiones) >= MAX_VERSIONES:
            a_eliminar = next((v for v in versiones if not v.es_resultado_modelo), None)
            if a_eliminar:
                a_eliminar.delete()

        nucleos      = sum(1 for o in objetos if o.get('tipo') == 'nucleo')
        micronucleos = sum(1 for o in objetos if o.get('tipo') == 'micronucleo')
        membranas    = sum(1 for o in objetos if o.get('tipo') == 'membrana')

        nuevo = AnalisisArchivos.objects.create(
            id_analisis_fk=analisis,
            contenido_json={'objetos': objetos},
            es_resultado_modelo=False,
            activo=True,
        )

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


# ============================================================================
# JOBS / SEGMENTACIÓN
# ============================================================================

def worker_analizar_caso(job_id):
    from django.db import connection as db_connection
    db_connection.close()

    try:
        job  = AnalisisJob.objects.get(id_job=job_id)
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

            except Exception as e:
                print(f"[Job {job_id}] Error muestra {muestra.id_muestra}: {e}")
                AnalisisJob.objects.filter(id_job=job_id).update(
                    procesadas=F('procesadas') + 1,
                    errores=F('errores') + 1,
                )

        job.refresh_from_db()
        estado_final = 'error' if job.errores == job.total_imagenes else 'completado'
        AnalisisJob.objects.filter(id_job=job_id).update(
            estado=estado_final,
            fecha_fin=timezone.now()
        )

    except Exception as e:
        AnalisisJob.objects.filter(id_job=job_id).update(
            estado='error',
            mensaje_error=str(e),
            fecha_fin=timezone.now()
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def iniciar_analisis(request, id_caso):
    try:
        caso = CasoClinico.objects.get(id_caso=id_caso)
    except CasoClinico.DoesNotExist:
        return Response({"error": "Caso no encontrado"}, status=404)

    job_activo = AnalisisJob.objects.filter(
        id_caso_fk=caso,
        estado__in=['pendiente', 'en_proceso']
    ).first()
    if job_activo:
        return Response({
            "error":    "Ya hay un análisis en progreso para este caso.",
            "job_id":   job_activo.id_job,
            "estado":   job_activo.estado,
            "progreso": job_activo.progreso_porcentaje,
            "es_reproceso": job_activo.es_reproceso,
        }, status=status.HTTP_409_CONFLICT)

    es_reproceso = request.data.get('reproceso', False)
    job = AnalisisJob.objects.create(
        id_caso_fk=caso,
        es_reproceso=es_reproceso,
    )

    hilo = threading.Thread(target=worker_analizar_caso, args=(job.id_job,), daemon=True)
    hilo.start()

    data = AnalisisJobSerializer(job).data
    data['job_id'] = job.id_job   # alias que usa el SideBar en lanzarAnalisis()
    return Response(data, status=status.HTTP_202_ACCEPTED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def estado_job(request, job_id):
    try:
        job = AnalisisJob.objects.get(id_job=job_id)
    except AnalisisJob.DoesNotExist:
        return Response({"error": "Job no encontrado"}, status=404)
    return Response(AnalisisJobSerializer(job).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def job_activo_caso(request, id_caso):
    # ¿Hay un job en curso?
    job_en_curso = AnalisisJob.objects.filter(
        id_caso_fk=id_caso,
        estado__in=['pendiente', 'en_proceso']
    ).order_by('-fecha_inicio').first()

    if job_en_curso:
        return Response({
            "hay_job_activo": True,
            "es_reproceso":   job_en_curso.es_reproceso,
            "job":            AnalisisJobSerializer(job_en_curso).data,
        })

    # No hay job activo — devolver el último job (para mostrar estado final)
    ultimo_job = AnalisisJob.objects.filter(
        id_caso_fk=id_caso,
    ).order_by('-fecha_inicio').first()

    # Calcular si el botón debe ser "reprocesar" (todas las muestras ya tienen análisis)
    total_muestras   = Muestra.objects.filter(id_caso_fk=id_caso).count()
    total_analizadas = Analisis.objects.filter(
        id_muestra_fk__id_caso_fk=id_caso,
        estado='listo'
    ).count()
    es_reproceso = (total_muestras > 0 and total_analizadas >= total_muestras)

    return Response({
        "hay_job_activo": False,
        "es_reproceso":   es_reproceso,
        "job":            AnalisisJobSerializer(ultimo_job).data if ultimo_job else None,
    })


# ============================================================================
# CARACTERIZACIÓN
# ============================================================================

def _distancia_euclidea(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


def _calcular_metricas_objeto(puntos):
    pts = np.array(puntos, dtype=np.float32)
    if len(pts) < 3:
        return None
    area      = float(abs(np.sum(pts[:-1, 0] * pts[1:, 1] - pts[1:, 0] * pts[:-1, 1])) / 2)
    perimeter = float(sum(_distancia_euclidea(pts[i], pts[(i+1) % len(pts)]) for i in range(len(pts))))
    roundness = float((4 * np.pi * area) / (perimeter ** 2)) if perimeter > 0 else 0
    centroid  = [float(np.mean(pts[:, 0])), float(np.mean(pts[:, 1]))]
    xs, ys    = pts[:, 0], pts[:, 1]
    major_axis = float(max(xs) - min(xs))
    minor_axis = float(max(ys) - min(ys))
    return {
        'area':       round(area, 3),
        'perimeter':  round(perimeter, 3),
        'roundness':  round(roundness, 4),
        'major_axis': round(major_axis, 3),
        'minor_axis': round(minor_axis, 3),
        'centroid':   centroid,
    }


def _caracterizar_muestra(objetos, id_muestra, idx_base=0):
    membranas    = [o for o in objetos if o.get('tipo') == 'membrana']
    nucleos      = [o for o in objetos if o.get('tipo') == 'nucleo']
    micronucleos = [o for o in objetos if o.get('tipo') == 'micronucleo']

    mem_met = []
    for mem in membranas:
        met = _calcular_metricas_objeto(mem.get('puntos', []))
        if met:
            mem_met.append(met)

    nuc_met = []
    for nuc in nucleos:
        met = _calcular_metricas_objeto(nuc.get('puntos', []))
        if met:
            nuc_met.append(met)

    mn_moa_params = []
    for mn in micronucleos:
        mn_met = _calcular_metricas_objeto(mn.get('puntos', []))
        if not mn_met:
            continue
        # Núcleo más cercano
        if nuc_met:
            dists  = [_distancia_euclidea(mn_met['centroid'], n['centroid']) for n in nuc_met]
            nucleo = nuc_met[int(np.argmin(dists))]
            fra_area     = round(mn_met['area'] / nucleo['area'], 4) if nucleo['area'] > 0 else 0
            borde_nuc    = nucleo['major_axis'] / 2
            borde_mn     = mn_met['major_axis'] / 2
            distance     = round(max(0, min(dists) - borde_nuc - borde_mn), 3)
            compactness  = round((mn_met['area'] ** 2) / (mn_met['perimeter'] ** 2), 4) if mn_met['perimeter'] > 0 else 0
        else:
            fra_area = compactness = distance = 0

        mn_moa_params.append({
            'area':        mn_met['area'],
            'roundness':   mn_met['roundness'],
            'compactness': compactness,
            'fra_area':    fra_area,
            'distance':    distance,
            'fra_intensity': None,
            'centroid':    mn_met['centroid'],
        })

    mn_por_membrana = [[] for _ in mem_met]
    for moa in mn_moa_params:
        dists_mem = [_distancia_euclidea(moa['centroid'], m['centroid']) for m in mem_met]
        idx_min   = int(np.argmin(dists_mem))
        mn_por_membrana[idx_min].append(moa)

    resultados = []
    for i, met in enumerate(mem_met):
        mns         = mn_por_membrana[i]
        mn_count    = len(mns)
        mn_area_tot = round(sum(mn['area'] for mn in mns), 3)
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
            'id_membrana':      idx_base + i + 1,
            'id_muestra':       id_muestra,
            'size':             met['area'],
            'circularity':      met['roundness'],
            'major_axis':       met['major_axis'],
            'minor_axis':       met['minor_axis'],
            'perimeter':        met['perimeter'],
            'mn_count':         mn_count,
            'mn_area':          mn_area_tot,
            'micronucleos_moa': mns_serializables,
            'intensity':        None,
        })

    return resultados


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def caracterizacion_caso(request, id_caso):
    try:
        caso = CasoClinico.objects.get(id_caso=id_caso)
    except CasoClinico.DoesNotExist:
        return Response({"error": "Caso no encontrado"}, status=404)

    muestras = Muestra.objects.filter(id_caso_fk=caso)

    resultados_membranas = []
    lista_imagenes = []
    idx = 0
    total_nucleos = 0
    total_micronucleos = 0
    total_membranas = 0

    for muestra in muestras:
        try:
            analisis = Analisis.objects.get(id_muestra_fk=muestra, estado='listo')
            archivo  = AnalisisArchivos.objects.get(id_analisis_fk=analisis, activo=True)
        except (Analisis.DoesNotExist, AnalisisArchivos.DoesNotExist):
            continue

        objetos = archivo.contenido_json.get("objetos", [])
        total_nucleos      += sum(1 for o in objetos if o.get('tipo') == 'nucleo')
        total_micronucleos += sum(1 for o in objetos if o.get('tipo') == 'micronucleo')
        total_membranas    += sum(1 for o in objetos if o.get('tipo') == 'membrana')

        if muestra.ruta_imagen:
            lista_imagenes.append({
                "id":       muestra.id_muestra,
                "title":    f"Muestra {muestra.id_muestra}",
                "src":      muestra.ruta_imagen.url,
                "mask_src": f"/api/mascaras/{analisis.id_analisis}/overlay/?offset={idx}"
            })

        datos = _caracterizar_muestra(objetos, muestra.id_muestra, idx)
        resultados_membranas.extend(datos)
        idx += len(datos)

    return Response({
        "totales": {
            "nucleos":       total_nucleos,
            "micronucleos":  total_micronucleos,
            "membranas":     total_membranas,
        },
        "membranas": resultados_membranas,
        "imagenes":  lista_imagenes,
    })