import requests
import os
import numpy as np
from datetime import datetime

FASTAPI_URL = "http://127.0.0.1:8001/api/segmentar"

# Configuración para modo simulado
USAR_DATOS_SIMULADOS = True  # Cambiar a False cuando FastAPI esté listo
CARPETA_MASCARAS_SIMULADAS = None  # Ruta a carpeta con máscaras .npy pregeneradas (opcional)


def llamar_microservicio(imagen_path):
    """
    Llama al microservicio FastAPI para procesar la imagen de muestra.
    Si FastAPI no está disponible, usa datos simulados.
    
    Args:
        imagen_path (str): Ruta completa al archivo de imagen
        
    Returns:
        dict: Respuesta con estructura:
            {
                "estado": "listo" | "error",
                "metricas": {
                    "total_celulas": int,
                    "micronucleos": int,
                    "celulas_binucleadas": int,
                    "celulas_normales": int,
                    "porcentaje_micronucleos": float
                },
                "archivo_npy": str (ruta al archivo .npy),
                "version_modelo": str
            }
    """
    print(f"🔄 Procesando imagen: {imagen_path}")
    
    # Verificar que el archivo existe
    if not os.path.exists(imagen_path):
        print(f"❌ El archivo no existe: {imagen_path}")
        return {
            "estado": "error",
            "metricas": {},
            "mensaje": f"Archivo no encontrado: {imagen_path}"
        }
    
    # Si está en modo simulado, usar datos simulados
    if USAR_DATOS_SIMULADOS:
        print("🎭 Usando datos simulados (FastAPI no configurado)")
        return generar_respuesta_simulada(imagen_path)
    
    # Intentar llamar a FastAPI
    try:
        with open(imagen_path, "rb") as f:
            files = {"file": (os.path.basename(imagen_path), f, "image/jpeg")}
            
            print(f"📤 Enviando imagen a FastAPI: {FASTAPI_URL}")
            response = requests.post(
                FASTAPI_URL,
                files=files,
                timeout=60
            )
        
        print(f"📥 Status code recibido: {response.status_code}")
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ Datos recibidos del microservicio: {data}")
        
        return data
        
    except requests.exceptions.ConnectionError as e:
        print(f"⚠️ No se pudo conectar a FastAPI, usando datos simulados")
        return generar_respuesta_simulada(imagen_path)
        
    except Exception as e:
        print(f"❌ Error al llamar FastAPI: {str(e)}")
        print("⚠️ Usando datos simulados como respaldo")
        return generar_respuesta_simulada(imagen_path)


def generar_respuesta_simulada(imagen_path):
    """
    Genera una respuesta simulada con métricas y máscara .npy
    """
    import random
    from django.conf import settings
    
    print("🎭 Generando respuesta simulada...")
    
    # Generar métricas simuladas realistas
    membranas = random.randint(30, 80) # Total de células
    celulas_binucleadas = random.randint(0, int(membranas * 0.05))
    celulas_trinucleadas = random.randint(0, int(membranas * 0.02))
    nucleos = membranas + celulas_binucleadas + (celulas_trinucleadas * 2)
    micronucleos = random.randint(0, int(nucleos * 0.15))
    
    metricas = {
        "nucleos": nucleos,
        "membranas": membranas,
        "micronucleos": micronucleos,
        "celulas_binucleadas": celulas_binucleadas,
        "celulas_trinucleadas":celulas_trinucleadas
    }
    
    # Generar o copiar máscara .npy
    mascara_path = generar_mascara_simulada(imagen_path)
    
    resultado = {
        "estado": "listo",
        "metricas": metricas,
        "archivo_npy": mascara_path,
        "version_modelo": "simulado_v1.0_beta",
        "timestamp_proceso": datetime.now().isoformat(),
        "simulado": True
    }
    
    print(f"✅ Respuesta simulada generada: {metricas}")
    return resultado


def generar_mascara_simulada(imagen_path):
    """
    Genera una máscara .npy simulada o copia una existente
    """
    from django.conf import settings
    import shutil
    
    # Crear directorio para máscaras simuladas si no existe
    mascaras_dir = os.path.join(settings.MEDIA_ROOT, 'mascaras', 'simuladas')
    os.makedirs(mascaras_dir, exist_ok=True)
    
    # Si hay carpeta con máscaras pregeneradas, copiar una aleatoria
    if CARPETA_MASCARAS_SIMULADAS and os.path.exists(CARPETA_MASCARAS_SIMULADAS):
        archivos_npy = [f for f in os.listdir(CARPETA_MASCARAS_SIMULADAS) if f.endswith('.npy')]
        if archivos_npy:
            import random
            mascara_original = os.path.join(CARPETA_MASCARAS_SIMULADAS, random.choice(archivos_npy))
            
            # Nombre único para la máscara
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nombre_mascara = f"mascara_sim_{timestamp}.npy"
            mascara_destino = os.path.join(mascaras_dir, nombre_mascara)
            
            # Copiar archivo
            shutil.copy(mascara_original, mascara_destino)
            print(f"📋 Máscara copiada: {mascara_original} -> {mascara_destino}")
            
            # Retornar ruta relativa a MEDIA_ROOT
            return os.path.relpath(mascara_destino, settings.MEDIA_ROOT)
    
    # Si no hay máscaras pregeneradas, crear una máscara dummy
    print("🎨 Generando máscara numpy simulada...")
    
    ancho, alto = 2456, 1842 
    
    # Creamos un fondo transparente (ceros)
    mascara_array = np.zeros((alto, ancho), dtype=np.uint8)

    # Dibujamos "células" grandes para que se noten
    for _ in range(20):
        cx = random.randint(100, ancho - 100)
        cy = random.randint(100, alto - 100)
        radio = random.randint(80, 150) # Círculos grandes
        
        y, x = np.ogrid[-cy:alto-cy, -cx:ancho-cx]
        mask_circulo = x*x + y*y <= radio*radio
        mascara_array[mask_circulo] = 1 # Valor para núcleos
    
    # Guardar como .npy
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    nombre_mascara = f"mascara_sim_{timestamp}.npy"
    mascara_path = os.path.join(mascaras_dir, nombre_mascara)
    
    np.save(mascara_path, mascara_array)
    print(f"✅ Máscara simulada creada: {mascara_path}")
    
    # Retornar ruta relativa a MEDIA_ROOT
    return os.path.relpath(mascara_path, settings.MEDIA_ROOT)


def configurar_carpeta_mascaras(ruta_carpeta):
    """
    Configura la carpeta donde están las máscaras pregeneradas
    
    Uso:
        from api.services.segmentacion_client import configurar_carpeta_mascaras
        configurar_carpeta_mascaras('/ruta/a/carpeta/mascaras')
    """
    global CARPETA_MASCARAS_SIMULADAS
    
    if os.path.exists(ruta_carpeta):
        CARPETA_MASCARAS_SIMULADAS = ruta_carpeta
        print(f"✅ Carpeta de máscaras configurada: {ruta_carpeta}")
    else:
        print(f"⚠️ La carpeta no existe: {ruta_carpeta}")


def activar_fastapi():
    """Desactiva el modo simulado para usar FastAPI real"""
    global USAR_DATOS_SIMULADOS
    USAR_DATOS_SIMULADOS = False
    print("✅ Modo FastAPI activado")


def activar_simulado():
    """Activa el modo simulado"""
    global USAR_DATOS_SIMULADOS
    USAR_DATOS_SIMULADOS = True
    print("✅ Modo simulado activado")