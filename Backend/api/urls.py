from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    PacienteViewSet,
    CasoClinicoViewSet,
    MuestraViewSet,
    AnalisisViewSet,
    MuestraCreateView,
    obtener_mascara_png,
    obtener_json_activo,
    guardar_edicion,
    # ___ HILOS ___
    iniciar_analisis,
    estado_job,
    job_activo_caso,
    # ___ CARACTERIZACIÓN ___
    caracterizacion_caso
)

router = DefaultRouter()
router.register(r'pacientes', PacienteViewSet)
router.register(r'casos',     CasoClinicoViewSet)
router.register(r'muestras',  MuestraViewSet)
router.register(r'analisis',  AnalisisViewSet)

urlpatterns = [

    # ── Endpoints manuales de análisis ──────────────────────────────────
    path(
        "mascaras/<int:id_analisis>/json/",
        obtener_json_activo,
        name="analisis-json-activo"
    ),
    path(
        "mascaras/<int:id_analisis>/<str:tipo_mascara>/",
        obtener_mascara_png,
        name='obtener-mascara-png'
    ),
    path(
        "analisis/<int:id_analisis>/editar/",
        guardar_edicion,
        name='guardar-edicion'
    ),
    path(
        "subir-muestra/",
        MuestraCreateView.as_view(),
        name='subir-muestra'
    ),
    path(
        "casos/<int:id_caso>/caracterizacion/",
        caracterizacion_caso,
        name="caracterizacion-caso"
    ),

    # ── Jobs / Segmentación ──────────────────────────────────────────────
    path(
        "casos/<int:id_caso>/analizar/",
        iniciar_analisis,
        name="iniciar-analisis"
    ),
    path(
        "casos/<int:id_caso>/job-activo/",
        job_activo_caso,
        name="job-activo-caso"
    ),
    path(
        "jobs/<int:job_id>/",
        estado_job,
        name="estado-job"
    ),

    # router
    path("", include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)