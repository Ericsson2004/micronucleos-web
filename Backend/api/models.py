from django.db import models

# Creacion de los modelos de la BD

class AnalisisPred(models.Model):
    id_analisis = models.AutoField(primary_key=True)
    id_paciente_fk = models.IntegerField()
    id_caso_fk = models.IntegerField()
    fecha = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Analisis {self.id_analisis}"

# PARTE DE LAS MUESTRAS DE SANGRE

# class MuestraSangre(models.Model):
    # id_muestra = models.AutoField(primary_key=True)
    # analisis = models.ForeignKey(
        # AnalisisPred,
        # on_delete=models.CASCADE,
        # related_name='muestras_sangre'
    # )
    # ruta_imagen = models.TextField()
    # observaciones = models.TextField(blank=True, null=True)

    # def __str__(self):
        # return f"Muestra Sangre {self.id_muestra}"

# PARTE DE LAS MUESTRAS DE SALIBA

class MuestraSaliva(models.Model):
    id_muestra = models.AutoField(primary_key=True)
    analisis = models.ForeignKey(
        AnalisisPred,
        on_delete=models.CASCADE,
        related_name='muestras_saliva'
    )
    imagen = models.ImageField(
        upload_to='muestras/saliva/%Y/%m/'
    )

    def __str__(self):
        return f"Muestra Saliva {self.id_muestra}"

class ResultadoAnalisis(models.Model):
    id_resultado = models.AutoField(primary_key=True)
    muestra = models.ForeignKey(
        MuestraSaliva,
        on_delete=models.CASCADE,
        related_name='resultados'
    )
    nucleos = models.IntegerField()
    micronucleos = models.IntegerField()
    membranas = models.IntegerField()

    def __str__(self):
        return f"Resultado {self.id_resultado}"

class AnalisisMascara(models.Model):
    id_mascara_analisis = models.AutoField(primary_key=True)
    resultado = models.ForeignKey(
        ResultadoAnalisis,
        on_delete=models.CASCADE,
        related_name='mascaras'
    )
    tipo_mascara = models.CharField(max_length=50)
    imagen = models.ImageField(
        upload_to='mascaras/saliva/%Y/%m/'
    )
    algoritmo = models.CharField(max_length=100)
    fecha_generacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Mascara {self.tipo_mascara} - Resultado {self.resultado.id_resultado}"
