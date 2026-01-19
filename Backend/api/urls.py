from django.urls import path
from .views import saludo
from .views import carga_analisis_dev
from rest_framework.routers import DefaultRouter
from .views import AnalisisPredViewSet

urlpatterns = [
    path('saludo/', saludo),
    path("dev/cargar-analisis/", carga_analisis_dev),
]

router = DefaultRouter()
router.register(r'analisis', AnalisisPredViewSet, basename='analisis')

urlpatterns = router.urls