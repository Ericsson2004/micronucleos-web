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
    MuestraCreateView
)

router = DefaultRouter()
router.register(r'pacientes', PacienteViewSet)
router.register(r'casos', CasoClinicoViewSet)
router.register(r'muestras', MuestraViewSet)
router.register(r'analisis', AnalisisViewSet)
router.register(r'ediciones', AnalisisEdicionViewSet)

urlpatterns = [
    path("subir-muestra/", MuestraCreateView.as_view(), name='subir-muestra'),
    path("", include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)