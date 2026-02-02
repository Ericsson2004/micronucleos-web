import os
import hashlib
from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

# ============================================================================
# UTILIDADES DE ARCHIVOS
# ============================================================================

def generar_nombre_estructurado(instance, filename, subcarpeta):
    """
    Genera la ruta: media/[subcarpeta]/YYYY/MM/nombre_formateado.ext
    Formato: [INICIALES]_[ID_CASO]_[TIPO]_[TIMESTAMP]_[HASH].[ext]
    """
    extension = os.path.splitext(filename)[1].lower()
    ahora = datetime.now()
    timestamp = ahora.strftime('%Y%m%d_%H%M%S')
    
    # 1. Obtener relación (Caso -> Paciente)
    # Dependiendo de si la instancia es Muestra o AnalisisArchivos
    if hasattr(instance, 'id_caso_fk'): # Es una Muestra
        caso = instance.id_caso_fk
        tipo_ref = instance.tipo_muestra.upper()
    else: # Es un AnalisisArchivo
        caso = instance.id_analisis_fk.id_muestra_fk.id_caso_fk
        tipo_ref = instance.tipo.upper()

    paciente = caso.id_paciente_fk
    
    # 2. Iniciales (Nombre + Apellido)
    ini_n = paciente.nombre[0].upper() if paciente.nombre else 'X'
    ini_a = paciente.apellido[0].upper() if paciente.apellido else 'X'
    iniciales = f"{ini_n}{ini_a}"

    # 3. ID Caso con padding
    id_caso_str = f"C{str(caso.id_caso).zfill(4)}"

    # 4. Hash corto del nombre original para evitar colisiones
    hash_txt = hashlib.md5(filename.encode()).hexdigest()[:6]

    # Construir nombre: AJ_C0001_SALIVA_20260202_123045_a1b2c3.png
    nombre_final = f"{iniciales}_{id_caso_str}_{tipo_ref}_{timestamp}_{hash_txt}{extension}"

    # Retornar ruta completa: media/[subcarpeta]/YYYY/MM/nombre
    return os.path.join(subcarpeta, ahora.strftime('%Y'), ahora.strftime('%m'), nombre_final)

def path_muestras(instance, filename):
    return generar_nombre_estructurado(instance, filename, 'muestras')

def path_mascaras(instance, filename):
    return generar_nombre_estructurado(instance, filename, 'mascaras')

# ============================================================================
# MODELOS
# ============================================================================

class Paciente(models.Model):
    id_paciente = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    identificacion = models.CharField(max_length=50, unique=True)
    fecha_nacimiento = models.DateField()
    email = models.EmailField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'paciente'

class CasoClinico(models.Model):
    ESTADO_CHOICES = [('abierto', 'Abierto'), ('en_proceso', 'En Proceso'), ('cerrado', 'Cerrado')]
    id_caso = models.AutoField(primary_key=True)
    id_paciente_fk = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='casos')
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='abierto')
    diagnostico = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'caso_clinico'

class Muestra(models.Model):
    TIPO_CHOICES = [('sangre', 'Sangre'), ('saliva', 'Saliva')]
    id_muestra = models.AutoField(primary_key=True)
    id_caso_fk = models.ForeignKey(CasoClinico, on_delete=models.CASCADE, related_name='muestras')
    tipo_muestra = models.CharField(max_length=20, choices=TIPO_CHOICES, default='saliva')
    # Uso de la función específica para muestras
    ruta_imagen = models.ImageField(upload_to=path_muestras)
    fecha_toma = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'muestras'

class Analisis(models.Model):
    ESTADO_CHOICES = [('pendiente', 'Pendiente'), ('proceso', 'En Proceso'), ('listo', 'Listo'), ('error', 'Error')]
    id_analisis = models.AutoField(primary_key=True)
    id_muestra_fk = models.ForeignKey(Muestra, on_delete=models.CASCADE, related_name='analisis')
    version_modelo = models.CharField(max_length=50)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    fecha_ejecucion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'analisis'

class AnalisisResultados(models.Model):
    id_resultado = models.AutoField(primary_key=True)
    id_analisis_fk = models.OneToOneField(Analisis, on_delete=models.CASCADE, related_name='resultados')
    # Aquí guardas los conteos y metadatos técnicos
    resultado_jsonb = models.JSONField()
    metadatos_jsonb = models.JSONField()
    fecha_generacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'analisis_resultados'

class AnalisisArchivos(models.Model):
    TIPO_ARCHIVO = [('mascara', 'Mascara'), ('json_raw', 'JSONB_Result'), ('preview', 'Preview')]
    id_archivo = models.AutoField(primary_key=True)
    id_analisis_fk = models.ForeignKey(Analisis, on_delete=models.CASCADE, related_name='archivos')
    tipo = models.CharField(max_length=20, choices=TIPO_ARCHIVO)
    # Uso de la función específica para máscaras y otros archivos
    ruta_archivo = models.FileField(upload_to=path_mascaras)

    class Meta:
        db_table = 'analisis_archivos'

class AnalisisEdicion(models.Model):
    id_edicion = models.AutoField(primary_key=True)
    id_analisis_fk = models.ForeignKey(Analisis, on_delete=models.CASCADE, related_name='ediciones')
    edicion_jsonb = models.JSONField() 
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'analisis_edicion'