from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    PacienteViewSet,
    CasoClinicoViewSet,
    MuestraViewSet,
    AnalisisViewSet,
    AnalisisEdicionViewSet,
    MuestraCreateView,
    obtener_mascara_png
)

router = DefaultRouter()
router.register(r'pacientes', PacienteViewSet)
router.register(r'casos', CasoClinicoViewSet)
router.register(r'muestras', MuestraViewSet)
router.register(r'analisis', AnalisisViewSet)
router.register(r'ediciones', AnalisisEdicionViewSet)

urlpatterns = [
    path(
        "analisis/<int:id_analisis>/mascara/<str:tipo_mascara>/",
        obtener_mascara_png,
        name='obtener-mascara-png'
    ),

    path("subir-muestra/", MuestraCreateView.as_view(), name='subir-muestra'),
    
    # Router al final
    path("", include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)