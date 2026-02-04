from rest_framework import serializers
from .models import (
    Paciente, CasoClinico, Muestra, 
    Analisis, AnalisisResultados, AnalisisArchivos, AnalisisEdicion
)

class PacienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paciente
        fields = '__all__'

class CasoClinicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CasoClinico
        fields = '__all__'

class MuestraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Muestra
        fields = '__all__'
        extra_kwargs = {
            'fecha_toma': {'required': False},
        }

class AnalisisResultadosSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalisisResultados
        fields = '__all__'

class AnalisisArchivosSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalisisArchivos
        fields = '__all__'

class AnalisisEdicionSerializer(serializers.ModelSerializer):
    # Mostramos el nombre del usuario que editó
    usuario_nombre = serializers.ReadOnlyField(source='usuario.username')

    class Meta:
        model = AnalisisEdicion
        fields = '__all__'

class MuestraMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Muestra
        fields = ['id_muestra', 'ruta_imagen', 'tipo_muestra', 'fecha_toma']

class AnalisisSerializer(serializers.ModelSerializer):
    # Relaciones anidadas para obtener info completa en una sola petición
    id_muestra_fk = MuestraMiniSerializer(read_only=True)
    resultados = AnalisisResultadosSerializer(read_only=True)
    archivos = AnalisisArchivosSerializer(many=True, read_only=True)
    ediciones = AnalisisEdicionSerializer(many=True, read_only=True)

    class Meta:
        model = Analisis
        fields = '__all__'