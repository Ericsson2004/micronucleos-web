import requests
import os
import numpy as np
from datetime import datetime
from django.conf import settings

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
                "mascaras": {
                    "nucleo": str (ruta al .npy),
                    "micronucleo": str (ruta al .npy),
                    "membrana": str (ruta al .npy)
                },
                "metricas": {
                    "nucleos": int,
                    "micronucleos": int,
                    "membranas": int,
                    "celulas_binucleadas": int,
                    "celulas_trinucleadas": int
                },
                "version_modelo": str
            }
    """
    print(f"📄 Procesando imagen: {imagen_path}")
    
    # Verificar que el archivo existe
    if not os.path.exists(imagen_path):
        print(f"❌ El archivo no existe: {imagen_path}")
        return {
            "estado": "error",
            "mascaras": {},
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
        print(f"✅ Datos recibidos del microservicio:")
        print(f"   - Máscaras: {list(data.get('mascaras', {}).keys())}")
        print(f"   - Métricas: {data.get('metricas', {})}")
        
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
    Genera una respuesta simulada con métricas y 3 máscaras .npy
    """
    import random
    
    print("🎭 Generando respuesta simulada...")
    
    # Generar métricas simuladas realistas
    membranas = random.randint(30, 80)  # Total de células
    celulas_binucleadas = random.randint(0, int(membranas * 0.05))
    celulas_trinucleadas = random.randint(0, int(membranas * 0.02))
    nucleos = membranas + celulas_binucleadas + (celulas_trinucleadas * 2)
    micronucleos = random.randint(0, int(nucleos * 0.15))
    
    metricas = {
        "nucleos": nucleos,
        "membranas": membranas,
        "micronucleos": micronucleos,
        "celulas_binucleadas": celulas_binucleadas,
        "celulas_trinucleadas": celulas_trinucleadas
    }
    
    # Generar o copiar las 3 máscaras .npy
    mascaras_paths = generar_mascaras_simuladas(imagen_path)
    
    resultado = {
        "estado": "listo",
        "mascaras": mascaras_paths,  # ✅ Ahora retorna dict con 3 rutas
        "metricas": metricas,
        "version_modelo": "simulado_v1.0_beta",
        "timestamp_proceso": datetime.now().isoformat(),
        "simulado": True
    }
    
    print(f"✅ Respuesta simulada generada:")
    print(f"   - Métricas: {metricas}")
    print(f"   - Máscaras: {list(mascaras_paths.keys())}")
    
    return resultado


def generar_mascaras_simuladas(imagen_path):
    """
    Genera 3 máscaras .npy simuladas o copia existentes.
    
    Returns:
        dict: {
            "nucleo": ruta_relativa,
            "micronucleo": ruta_relativa,
            "membrana": ruta_relativa
        }
    """
    import random
    import shutil
    
    # Crear directorio para máscaras simuladas si no existe
    mascaras_dir = os.path.join(settings.MEDIA_ROOT, 'mascaras', 'simuladas')
    os.makedirs(mascaras_dir, exist_ok=True)
    
    mascaras_paths = {}
    tipos = ['nucleo', 'micronucleo', 'membrana']
    
    # Si hay carpeta con máscaras pregeneradas
    if CARPETA_MASCARAS_SIMULADAS and os.path.exists(CARPETA_MASCARAS_SIMULADAS):
        print(f"📂 Buscando máscaras en: {CARPETA_MASCARAS_SIMULADAS}")
        
        for tipo in tipos:
            # Buscar archivos que contengan el tipo en el nombre
            archivos_tipo = [
                f for f in os.listdir(CARPETA_MASCARAS_SIMULADAS) 
                if tipo in f.lower() and f.endswith('.npy')
            ]
            
            if archivos_tipo:
                # Tomar un archivo aleatorio de este tipo
                mascara_original = os.path.join(
                    CARPETA_MASCARAS_SIMULADAS, 
                    random.choice(archivos_tipo)
                )
                
                # Nombre único para la máscara
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                nombre_mascara = f"{tipo}_sim_{timestamp}.npy"
                mascara_destino = os.path.join(mascaras_dir, nombre_mascara)
                
                # Copiar archivo
                shutil.copy(mascara_original, mascara_destino)
                print(f"📋 Máscara {tipo} copiada: {os.path.basename(mascara_original)}")
                
                # Guardar ruta relativa
                mascaras_paths[tipo] = os.path.relpath(mascara_destino, settings.MEDIA_ROOT)
            else:
                print(f"⚠️ No se encontró máscara pregenerada para {tipo}, generando...")
                mascaras_paths[tipo] = generar_mascara_dummy(tipo, mascaras_dir)
    else:
        # Generar las 3 máscaras dummy
        print("🎨 Generando máscaras numpy simuladas...")
        for tipo in tipos:
            mascaras_paths[tipo] = generar_mascara_dummy(tipo, mascaras_dir)
    
    return mascaras_paths


def generar_mascara_dummy(tipo, directorio_salida):
    """
    Genera una máscara dummy para un tipo específico.
    
    Args:
        tipo: "nucleo", "micronucleo", o "membrana"
        directorio_salida: Directorio donde guardar el archivo
    
    Returns:
        str: Ruta relativa a MEDIA_ROOT
    """
    import random
    
    ancho, alto = 2456, 1842
    
    # Crear máscara vacía
    mascara_array = np.zeros((alto, ancho), dtype=np.uint8)
    
    # Parámetros según el tipo
    if tipo == 'nucleo':
        num_objetos = random.randint(30, 60)
        radio_min, radio_max = 80, 150
        color = 1
    elif tipo == 'micronucleo':
        num_objetos = random.randint(0, 10)
        radio_min, radio_max = 20, 40
        color = 1
    else:  # membrana
        num_objetos = random.randint(25, 55)
        radio_min, radio_max = 120, 200
        color = 1
    
    # Dibujar objetos
    for i in range(num_objetos):
        cx = random.randint(radio_max, ancho - radio_max)
        cy = random.randint(radio_max, alto - radio_max)
        radio = random.randint(radio_min, radio_max)
        
        y, x = np.ogrid[-cy:alto-cy, -cx:ancho-cx]
        mask_circulo = x*x + y*y <= radio*radio
        
        # Usar ID único para cada objeto (en vez de 1 para todos)
        mascara_array[mask_circulo] = i + 1
    
    # Guardar como .npy
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:18]  # Incluir microsegundos
    nombre_mascara = f"{tipo}_sim_{timestamp}.npy"
    mascara_path = os.path.join(directorio_salida, nombre_mascara)
    
    np.save(mascara_path, mascara_array)
    print(f"✅ Máscara {tipo} creada: {num_objetos} objetos")
    
    # Retornar ruta relativa a MEDIA_ROOT
    return os.path.relpath(mascara_path, settings.MEDIA_ROOT)


def configurar_carpeta_mascaras(ruta_carpeta):
    """
    Configura la carpeta donde están las máscaras pregeneradas.
    
    Estructura esperada:
    ruta_carpeta/
        ├── nucleo_001.npy
        ├── micronucleo_001.npy
        ├── membrana_001.npy
        ├── nucleo_002.npy
        └── ...
    
    Los archivos deben tener el tipo (nucleo, micronucleo, membrana) en el nombre.
    
    Uso:
        from api.services.segmentacion_client import configurar_carpeta_mascaras
        configurar_carpeta_mascaras('/ruta/a/carpeta/mascaras')
    """
    global CARPETA_MASCARAS_SIMULADAS
    
    if os.path.exists(ruta_carpeta):
        CARPETA_MASCARAS_SIMULADAS = ruta_carpeta
        
        # Verificar que tenga archivos .npy
        archivos_npy = [f for f in os.listdir(ruta_carpeta) if f.endswith('.npy')]
        
        print(f"✅ Carpeta de máscaras configurada: {ruta_carpeta}")
        print(f"   - Archivos encontrados: {len(archivos_npy)}")
        
        # Mostrar resumen por tipo
        tipos = ['nucleo', 'micronucleo', 'membrana']
        for tipo in tipos:
            count = len([f for f in archivos_npy if tipo in f.lower()])
            print(f"   - {tipo.capitalize()}: {count} archivos")
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


# ============================================================================
# FUNCIÓN PARA USAR MÁSCARAS PREGENERADAS ESPECÍFICAS
# ============================================================================

def usar_mascaras_especificas(ruta_nucleo, ruta_micronucleo, ruta_membrana):
    """
    Usa máscaras específicas que ya tienes generadas.
    
    Args:
        ruta_nucleo: Ruta absoluta al archivo nucleo.npy
        ruta_micronucleo: Ruta absoluta al archivo micronucleo.npy
        ruta_membrana: Ruta absoluta al archivo membrana.npy
    
    Returns:
        dict: Respuesta formateada para el backend
    
    Ejemplo de uso:
        resultado = usar_mascaras_especificas(
            '/path/to/nucleo.npy',
            '/path/to/micronucleo.npy',
            '/path/to/membrana.npy'
        )
    """
    # Verificar que los archivos existen
    rutas = {
        'nucleo': ruta_nucleo,
        'micronucleo': ruta_micronucleo,
        'membrana': ruta_membrana
    }
    
    for tipo, ruta in rutas.items():
        if not os.path.exists(ruta):
            print(f"❌ Archivo no encontrado: {ruta}")
            return {
                "estado": "error",
                "mensaje": f"Archivo {tipo}.npy no encontrado",
                "mascaras": {},
                "metricas": {}
            }
    
    # Calcular métricas reales desde las máscaras
    metricas = calcular_metricas_desde_mascaras(rutas)
    
    return {
        "estado": "listo",
        "mascaras": rutas,  # Rutas absolutas
        "metricas": metricas,
        "version_modelo": "pregenerado_manual_v1.0",
        "timestamp_proceso": datetime.now().isoformat(),
        "fuente": "mascaras_pregeneradas"
    }


def calcular_metricas_desde_mascaras(rutas_mascaras):
    """
    Calcula métricas reales a partir de archivos .npy.
    
    Args:
        rutas_mascaras: dict con rutas a los 3 archivos NPY
    
    Returns:
        dict: métricas calculadas
    """
    metricas = {
        "nucleos": 0,
        "micronucleos": 0,
        "membranas": 0,
        "celulas_binucleadas": 0,
        "celulas_trinucleadas": 0
    }
    
    try:
        # Cargar máscaras
        mask_nucleo = np.load(rutas_mascaras['nucleo'])
        mask_micro = np.load(rutas_mascaras['micronucleo'])
        mask_membrana = np.load(rutas_mascaras['membrana'])
        
        # Contar objetos únicos (cada objeto tiene un ID diferente)
        metricas['nucleos'] = len(np.unique(mask_nucleo)) - 1  # -1 para excluir fondo (0)
        metricas['micronucleos'] = len(np.unique(mask_micro)) - 1
        metricas['membranas'] = len(np.unique(mask_membrana)) - 1
        
        # Calcular células binucleadas
        if metricas['membranas'] > 0 and metricas['nucleos'] > metricas['membranas']:
            diferencia = metricas['nucleos'] - metricas['membranas']
            metricas['celulas_binucleadas'] = min(diferencia, metricas['membranas'])
        
        print(f"📊 Métricas calculadas desde máscaras:")
        for key, val in metricas.items():
            print(f"   - {key}: {val}")
        
    except Exception as e:
        print(f"❌ Error calculando métricas: {e}")
    
    return metricas