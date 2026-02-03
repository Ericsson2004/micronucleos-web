import os
import hashlib
from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

# ============================================================================
# UTILIDADES DE ARCHIVOS
# ============================================================================

def generar_nombre_estructurado(instance, filename, subcarpeta, tipo_mascara=None):
    """
    Genera la ruta: media/[subcarpeta]/[tipo_muestra]/YYYY/MM/nombre_formateado.ext
    Formato: [INICIALES]_[ID_CASO]_[TIPO]_[TIMESTAMP]_[HASH].[ext]
    """
    extension = os.path.splitext(filename)[1].lower()
    ahora = datetime.now()
    timestamp = ahora.strftime('%Y%m%d_%H%M%S')
    
    # 1. Obtener relación (Caso -> Paciente)
    if hasattr(instance, 'id_caso_fk'):  # Es una Muestra
        caso = instance.id_caso_fk
        tipo_ref = instance.tipo_muestra.upper()
        tipo_muestra_path = instance.tipo_muestra.lower()
    else:  # Es un AnalisisArchivo
        caso = instance.id_analisis_fk.id_muestra_fk.id_caso_fk
        tipo_muestra_path = instance.id_analisis_fk.id_muestra_fk.tipo_muestra.lower()
        
        # Para máscaras, usar el tipo específico (NUCLEO, MICRONUCLEO, MEMBRANA)
        if tipo_mascara:
            tipo_ref = tipo_mascara
        else:
            tipo_ref = instance.tipo.upper().replace('MASCARA_', '')

    paciente = caso.id_paciente_fk
    
    # 2. Iniciales (Nombre + Apellido)
    ini_n = paciente.nombre[0].upper() if paciente.nombre else 'X'
    ini_a = paciente.apellido[0].upper() if paciente.apellido else 'X'
    iniciales = f"{ini_n}{ini_a}"

    # 3. ID Caso con padding
    id_caso_str = f"C{str(caso.id_caso).zfill(4)}"

    # 4. Hash corto del nombre original para evitar colisiones
    hash_txt = hashlib.md5(filename.encode()).hexdigest()[:6]

    # Construir nombre: AJ_C0001_NUCLEO_20260202_123045_a1b2c3.npy
    nombre_final = f"{iniciales}_{id_caso_str}_{tipo_ref}_{timestamp}_{hash_txt}{extension}"

    # Retornar ruta completa: media/[subcarpeta]/[tipo_muestra]/YYYY/MM/nombre
    return os.path.join(
        subcarpeta, 
        tipo_muestra_path, 
        ahora.strftime('%Y'), 
        ahora.strftime('%m'), 
        nombre_final
    )


def path_muestras(instance, filename):
    """Ruta para imágenes de muestras originales"""
    return generar_nombre_estructurado(instance, filename, 'muestras')


def path_mascaras(instance, filename):
    """
    Ruta para archivos de máscaras NPY.
    El tipo específico (NUCLEO, MICRONUCLEO, MEMBRANA) se determina del campo 'tipo'
    """
    # Extraer el tipo de máscara del campo tipo
    tipo_mascara = None
    if hasattr(instance, 'tipo'):
        if 'nucleo' in instance.tipo.lower():
            if 'micro' in instance.tipo.lower():
                tipo_mascara = 'MICRONUCLEO'
            else:
                tipo_mascara = 'NUCLEO'
        elif 'membrana' in instance.tipo.lower():
            tipo_mascara = 'MEMBRANA'
    
    return generar_nombre_estructurado(instance, filename, 'mascaras', tipo_mascara)


def path_previews(instance, filename):
    """Ruta para imágenes preview (PNG con overlay de máscaras)"""
    return generar_nombre_estructurado(instance, filename, 'previews')


def path_json_raw(instance, filename):
    """Ruta para archivos JSON raw del microservicio"""
    return generar_nombre_estructurado(instance, filename, 'json_raw')


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
    
    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.identificacion})"


class CasoClinico(models.Model):
    ESTADO_CHOICES = [
        ('abierto', 'Abierto'), 
        ('en_proceso', 'En Proceso'), 
        ('cerrado', 'Cerrado')
    ]
    
    id_caso = models.AutoField(primary_key=True)
    id_paciente_fk = models.ForeignKey(
        Paciente, 
        on_delete=models.CASCADE, 
        related_name='casos'
    )
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='abierto')
    diagnostico = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'caso_clinico'
    
    def __str__(self):
        return f"Caso {self.id_caso} - {self.id_paciente_fk.nombre}"


class Muestra(models.Model):
    TIPO_CHOICES = [
        ('sangre', 'Sangre'), 
        ('saliva', 'Saliva')
    ]
    
    id_muestra = models.AutoField(primary_key=True)
    id_caso_fk = models.ForeignKey(
        CasoClinico, 
        on_delete=models.CASCADE, 
        related_name='muestras'
    )
    tipo_muestra = models.CharField(max_length=20, choices=TIPO_CHOICES, default='saliva')
    ruta_imagen = models.ImageField(upload_to=path_muestras)
    fecha_toma = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'muestras'
    
    def __str__(self):
        return f"Muestra {self.id_muestra} ({self.tipo_muestra})"


class Analisis(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'), 
        ('proceso', 'En Proceso'), 
        ('listo', 'Listo'), 
        ('error', 'Error')
    ]
    
    id_analisis = models.AutoField(primary_key=True)
    id_muestra_fk = models.ForeignKey(
        Muestra, 
        on_delete=models.CASCADE, 
        related_name='analisis'
    )
    version_modelo = models.CharField(max_length=50)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    fecha_ejecucion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'analisis'
    
    def __str__(self):
        return f"Análisis {self.id_analisis} - {self.estado}"


class AnalisisResultados(models.Model):
    id_resultado = models.AutoField(primary_key=True)
    id_analisis_fk = models.OneToOneField(
        Analisis, 
        on_delete=models.CASCADE, 
        related_name='resultados'
    )
    # Conteos y métricas técnicas (ej: num_nucleos, num_micronucleos, etc.)
    resultado_jsonb = models.JSONField()
    # Metadata del procesamiento (versión, timestamp, parámetros, etc.)
    metadatos_jsonb = models.JSONField()
    fecha_generacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'analisis_resultados'
    
    def __str__(self):
        return f"Resultado {self.id_resultado} - Análisis {self.id_analisis_fk.id_analisis}"


class AnalisisArchivos(models.Model):
    """
    Almacena los archivos generados por el análisis.
    Cada tipo de máscara (núcleo, micronúcleo, membrana) es un registro separado.
    """
    TIPO_ARCHIVO = [
        ('mascara_nucleo', 'Máscara Núcleo'),
        ('mascara_micronucleo', 'Máscara Micronúcleo'),
        ('mascara_membrana', 'Máscara Membrana'),
        ('preview', 'Preview PNG'),
        ('json_raw', 'JSON Raw')
    ]
    
    id_archivo = models.AutoField(primary_key=True)
    id_analisis_fk = models.ForeignKey(
        Analisis, 
        on_delete=models.CASCADE, 
        related_name='archivos'
    )
    tipo = models.CharField(max_length=30, choices=TIPO_ARCHIVO)
    
    # Función de upload dinámica según el tipo
    ruta_archivo = models.FileField(upload_to=path_mascaras)
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'analisis_archivos'
        # Opcional: Prevenir duplicados (un análisis solo puede tener una máscara de cada tipo)
        unique_together = [['id_analisis_fk', 'tipo']]
    
    def __str__(self):
        return f"{self.tipo} - Análisis {self.id_analisis_fk.id_analisis}"
    
    def save(self, *args, **kwargs):
        """Override save para usar diferentes path_* según el tipo"""
        # Si estamos creando el objeto y tiene un archivo
        if not self.pk and self.ruta_archivo:
            # Cambiar dinámicamente la función upload_to
            if self.tipo in ['mascara_nucleo', 'mascara_micronucleo', 'mascara_membrana']:
                self._meta.get_field('ruta_archivo').upload_to = path_mascaras
            elif self.tipo == 'preview':
                self._meta.get_field('ruta_archivo').upload_to = path_previews
            elif self.tipo == 'json_raw':
                self._meta.get_field('ruta_archivo').upload_to = path_json_raw
        
        super().save(*args, **kwargs)


class AnalisisEdicion(models.Model):
    """
    Registro de ediciones manuales realizadas sobre los resultados del análisis.
    Permite auditoría y reversión de cambios.
    """
    id_edicion = models.AutoField(primary_key=True)
    id_analisis_fk = models.ForeignKey(
        Analisis, 
        on_delete=models.CASCADE, 
        related_name='ediciones'
    )
    # Cambios realizados (ej: {"celulas_modificadas": [1,2,3], "accion": "eliminar"})
    edicion_jsonb = models.JSONField()
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)  # Permite desactivar ediciones antiguas

    class Meta:
        db_table = 'analisis_edicion'
        ordering = ['-fecha']  # Más recientes primero
    
    def __str__(self):
        return f"Edición {self.id_edicion} por {self.usuario} - {self.fecha}"