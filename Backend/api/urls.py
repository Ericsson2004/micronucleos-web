from django.urls import path
from .views import saludo
from .views import carga_analisis_dev

urlpatterns = [
    path('saludo/', saludo),
    path("dev/cargar-analisis/", carga_analisis_dev),
]
