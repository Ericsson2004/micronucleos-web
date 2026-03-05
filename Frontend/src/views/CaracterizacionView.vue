<template>
  <div class="characterization-portal">
    <div class="patient-info-bar">
      <div class="info">
        <strong>Paciente:</strong> {{ patientData.name }} |
        <strong>Case ID:</strong> {{ patientData.caseId }} |
        <strong>Fecha:</strong> {{ patientData.date }}
      </div>
      <div class="search-bar">
        <input type="text" placeholder="Buscar..." />
        <button class="icon-btn">🔍</button>
        <button class="icon-btn">⚙️</button>
      </div>
    </div>

    <main class="main-content">

      <section class="image-viewer-section">
        <div class="section-header">
          <h2>{{ currentImage.title }}</h2>
          <div class="nav-arrows">
            <button class="arrow-btn">&lt;</button>
            <button class="arrow-btn">&gt;</button>
          </div>
        </div>

        <div class="main-image-container">
          <img :src="currentImage.src" alt="Análisis de Micronúcleos" class="main-image" />
          <div class="legend">
            <div><span class="color-box blue"></span> = núcleo</div>
            <div><span class="color-box red"></span> = micronúcleo</div>
          </div>
        </div>

        <div class="thumbnails">
          <button
            v-for="(img, index) in imageList"
            :key="index"
            class="thumbnail"
            :class="{ active: currentImage.id === img.id }"
            @click="selectImage(img)"
          >
            <p>{{ img.title }}</p>
            <img :src="img.src" :alt="img.title" />
          </button>
        </div>
      </section>

      <section class="results-section">
        <h2>Resultados del Análisis de Membrana - {{ currentImage.title }}</h2>

        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th>ID Membrana</th>
                <th>Tamaño (µm³)</th>
                <th>Circularidad</th>
                <th>Eje Mayor (µm)</th>
                <th>Eje Menor (µm)</th>
                <th>Perímetro (µm)</th>
                <th>Conteo µN</th>
                <th>Área µN (µm²)</th>
                <th>Intensidad Media</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in tableData" :key="row.id">
                <td>#{{ row.id }}</td>
                <td>{{ row.size }}</td>
                <td>{{ row.circularity }}</td>
                <td>{{ row.majorAxis }}</td>
                <td>{{ row.minorAxis }}</td>
                <td>{{ row.perimeter }}</td>
                <td>{{ row.mnCount }}</td>
                <td>{{ row.mnArea }}</td>
                <td>{{ row.intensity }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="action-buttons">
          <button class="btn-secondary">Exportar Resultados</button>
          <button class="btn-primary">Analizar Caso</button>
        </div>
      </section>

    </main>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';

// 1. Definimos las propiedades que recibimos de App.vue
const props = defineProps({
  patientId: {
    type: [Number, String],
    default: null
  },
  caseId: {
    type: [Number, String],
    default: null
  }
});

//const emit = defineEmits(['update-patient', 'update-case']);

const patientData = ref({
  name: 'Selecciona o busca un paciente',
  caseId: '-',
  date: '-'
});

watch(() => props.patientId, (newId) => {
  if (newId) {
    console.log("Cargando datos en Caracterización para el Paciente ID:", newId);
    patientData.value = {
      name: `Paciente #${newId} (Heredado de Segmentación)`,
      caseId: props.caseId || 'Sin caso',
      date: new Date().toLocaleDateString()
    };

  }
}, { immediate: true });


const imageList = ref([
  { id: 1, title: 'Image 1', src: 'https://placehold.co/600x400/e0e0e0/808080?text=Células+Segmentadas+1' },
  { id: 2, title: 'Image 2', src: 'https://placehold.co/600x400/e0e0e0/808080?text=Células+Segmentadas+2' },
  { id: 3, title: 'Image 3', src: 'https://placehold.co/600x400/e0e0e0/808080?text=Células+Segmentadas+3' }
]);

const currentImage = ref(imageList.value[0]);

const selectImage = (img) => {
  currentImage.value = img;
};

const tableData = ref([
  { id: 1, size: 25.4, circularity: 0.88, majorAxis: 10.2, minorAxis: 7.1, perimeter: 35.6, mnCount: 2, mnArea: 5.1, intensity: 120 },
  { id: 2, size: 25.4, circularity: 0.88, majorAxis: 10.2, minorAxis: 7.1, perimeter: 35.6, mnCount: 2, mnArea: 5.1, intensity: 120 },
  { id: 3, size: 25.4, circularity: 0.88, majorAxis: 10.2, minorAxis: 7.1, perimeter: 35.6, mnCount: 2, mnArea: 5.1, intensity: 120 },
  { id: 4, size: 25.4, circularity: 0.88, majorAxis: 10.2, minorAxis: 7.1, perimeter: 35.6, mnCount: 2, mnArea: 5.1, intensity: 120 },
  { id: 5, size: 25.4, circularity: 0.88, majorAxis: 11.2, minorAxis: 7.1, perimeter: 35.6, mnCount: 2, mnArea: 5.1, intensity: 120 },
  { id: 10, size: 19.6, circularity: 0.88, majorAxis: 9.8, minorAxis: 5.6, perimeter: 35.6, mnCount: 2, mnArea: 5.1, intensity: 120 },
]);
</script>

<style scoped>
/* Convertimos el contenedor principal en flexbox de altura 100% */
.characterization-portal {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  color: #333;
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}

/* Evitamos que la barra superior se aplaste */
.patient-info-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: white;
  padding: 12px 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  margin-bottom: 20px;
  font-size: 0.95rem;
  border: 1px solid #e0e0e0;
  flex-shrink: 0;
}

.search-bar {
  display: flex;
  gap: 8px;
}

.search-bar input {
  padding: 6px 12px;
  border: 1px solid #ccc;
  border-radius: 6px;
  outline: none;
}

.search-bar input:focus {
  border-color: #667eea;
}

.icon-btn {
  background: none;
  border: 1px solid #ccc;
  border-radius: 6px;
  cursor: pointer;
  padding: 4px 8px;
  background-color: #f8f9fa;
}

/* main-content toma todo el espacio restante dinámicamente */
.main-content {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 20px;
  flex: 1;
  min-height: 0; /* Necesario para que grid/flexbox no se desborden */
}

/* Las secciones laterales también ocupan el 100% de su cuadrícula */
.image-viewer-section, .results-section {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  display: flex;
  flex-direction: column;
  border: 1px solid #e0e0e0;
  min-height: 0;
}

.section-header, .results-section h2, .action-buttons, .thumbnails {
  flex-shrink: 0; /* Evita que estos elementos se encojan */
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.section-header h2, .results-section h2 {
  font-size: 1.1rem;
  margin: 0;
  margin-bottom: 15px;
  color: #2c3e50;
  font-weight: 600;
}

.arrow-btn {
  background: #f0f4f8;
  border: none;
  padding: 4px 12px;
  margin-left: 5px;
  border-radius: 4px;
  cursor: pointer;
}

/* Contenedor de imagen toma el espacio sobrante */
.main-image-container {
  position: relative;
  width: 100%;
  background-color: #eee;
  border-radius: 6px;
  overflow: hidden;
  margin-bottom: 20px;
  flex: 1;
  min-height: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* La imagen se ajusta sin deformarse (contain) */
.main-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.legend {
  position: absolute;
  bottom: 15px;
  right: 15px;
  background: rgba(255, 255, 255, 0.95);
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 0.85rem;
  border: 1px solid #ccc;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.color-box {
  display: inline-block;
  width: 12px;
  height: 12px;
  margin-right: 5px;
  vertical-align: middle;
  border-radius: 2px;
}
.color-box.blue { background-color: #3b82f6; }
.color-box.red { background-color: #ef4444; }

.thumbnails {
  display: flex;
  gap: 15px;
  justify-content: center;
}

.thumbnail {
  background: none;
  border: 2px solid transparent;
  cursor: pointer;
  padding: 4px;
  border-radius: 6px;
  text-align: center;
  transition: border-color 0.2s;
}

.thumbnail.active {
  border-color: #667eea;
  background-color: #f0f4f8;
}

.thumbnail img {
  width: 90px;
  height: 60px;
  object-fit: cover;
  border-radius: 4px;
}

.thumbnail p {
  font-size: 0.8rem;
  margin: 0 0 6px 0;
  color: #4b5563;
}

/* La tabla toma el espacio libre y tiene su propio scroll */
.table-container {
  flex: 1;
  overflow-y: auto;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  margin-bottom: 20px;
  min-height: 0; /* Crucial para que funcione el overflow flexbox */
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
  text-align: center;
}

thead {
  background-color: #f8f9fa;
  position: sticky;
  top: 0;
  box-shadow: 0 1px 0 #e0e0e0;
}

th, td {
  padding: 10px;
  border-bottom: 1px solid #e0e0e0;
}

th {
  font-weight: 600;
  color: #4b5563;
}

.action-buttons {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.btn-primary, .btn-secondary {
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  border: none;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}

.btn-secondary {
  background-color: white;
  color: #4b5563;
  border: 1px solid #ccc;
}

.btn-secondary:hover {
  background-color: #f8f9fa;
  color: #2c3e50;
}
</style>
