from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def saludo(request):
    return Response({
        "mensaje": "Hola desde Django API",
        "status": "ok"
    })

# CARGA DE DATOS
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.viewsets import ReadOnlyModelViewSet
from .serializers import AnalisisPredSerializer

from .models import (
    AnalisisPred,
    MuestraSaliva,
    ResultadoAnalisis,
    AnalisisMascara
)

class AnalisisPredViewSet(ReadOnlyModelViewSet):
    queryset = AnalisisPred.objects.all().order_by('-fecha')
    serializer_class = AnalisisPredSerializer

@csrf_exempt
def carga_analisis_dev(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        analisis = AnalisisPred.objects.create(
            id_paciente_fk=request.POST.get("id_paciente_fk"),
            id_caso_fk=request.POST.get("id_caso_fk"),
        )

        muestra = MuestraSaliva.objects.create(
            analisis=analisis,
            imagen=request.FILES.get("muestra_imagen")
        )

        resultado = ResultadoAnalisis.objects.create(
            muestra=muestra,
            nucleos=request.POST.get("nucleos"),
            micronucleos=request.POST.get("micronucleos"),
            membranas=request.POST.get("membranas"),
        )

        if request.FILES.get("mascara_imagen"):
            AnalisisMascara.objects.create(
                resultado=resultado,
                tipo_mascara=request.POST.get("tipo_mascara"),
                algoritmo=request.POST.get("algoritmo"),
                imagen=request.FILES.get("mascara_imagen")
            )

        return JsonResponse({"ok": True})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)