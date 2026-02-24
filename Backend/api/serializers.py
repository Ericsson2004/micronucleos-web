from rest_framework import serializers
from .models import (
    Paciente, CasoClinico, Muestra, 
    Analisis, AnalisisResultados, AnalisisArchivos,
    AnalisisJob 
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
        read_only_fields = [
            'version',
            'activo',
            'fecha_creacion',
            'usuario_creacion'
        ]

class MuestraMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Muestra
        fields = ['id_muestra', 'ruta_imagen', 'thumbnail', 'tipo_muestra', 'fecha_toma']

class AnalisisSerializer(serializers.ModelSerializer):
    id_muestra_fk = MuestraMiniSerializer(read_only=True)
    resultados    = AnalisisResultadosSerializer(read_only=True)
    archivos      = AnalisisArchivosSerializer(many=True, read_only=True)

    class Meta:
        model  = Analisis
        fields = '__all__'

class AnalisisJobSerializer(serializers.ModelSerializer):
    # Campo calculado (property del modelo) — solo lectura
    progreso_porcentaje = serializers.IntegerField(read_only=True)

    class Meta:
        model  = AnalisisJob
        fields = [
            'id_job',
            'id_caso_fk',
            'estado',
            'total_imagenes',
            'procesadas',
            'errores',
            'progreso_porcentaje',   # calculado
            'es_reproceso',
            'version_modelo',
            'mensaje_error',
            'fecha_inicio',
            'fecha_fin',
        ]
        read_only_fields = [
            'estado', 'total_imagenes', 'procesadas', 'errores',
            'progreso_porcentaje', 'mensaje_error', 'fecha_inicio', 'fecha_fin',
        ]