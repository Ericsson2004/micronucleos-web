from rest_framework import serializers
from .models import (
    AnalisisPred,
    MuestraSaliva,
    ResultadoAnalisis,
    AnalisisMascara
)

class AnalisisMascaraSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalisisMascara
        fields = '__all__'


class ResultadoAnalisisSerializer(serializers.ModelSerializer):
    mascaras = AnalisisMascaraSerializer(many=True, read_only=True)

    class Meta:
        model = ResultadoAnalisis
        fields = '__all__'


class MuestraSalivaSerializer(serializers.ModelSerializer):
    resultados = ResultadoAnalisisSerializer(many=True, read_only=True)

    class Meta:
        model = MuestraSaliva
        fields = '__all__'


class AnalisisPredSerializer(serializers.ModelSerializer):
    muestras_saliva = MuestraSalivaSerializer(many=True, read_only=True)

    class Meta:
        model = AnalisisPred
        fields = '__all__'
