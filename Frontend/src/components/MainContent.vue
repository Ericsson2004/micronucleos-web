<template>
  <main class="content">

    <!-- HEADER -->
    <header class="page-header">
      <h2>
        Resultados del Análisis:
        <span v-if="patientId">
          Paciente [{{ patientId }}]
          <span v-if="caseId"> &gt; Caso [{{ caseId }}]</span>
        </span>
        <span v-else class="muted">
          Seleccione un paciente y un caso
        </span>
      </h2>

      <div class="header-actions">
        <button class="btn-outline">⬇ Reporte CSV</button>
        <button class="btn-outline">📄 PDF</button>
      </div>
    </header>

    <div class="layout-grid">

      <!-- GALERÍA -->
      <div class="gallery-column">
        <div
          v-for="muestra in imagenes"
          :key="muestra.id_muestra"
          class="thumb"
          :class="{ active: muestra === imagenSeleccionada }"
          @click="imagenSeleccionada = muestra"
        >
          <img
            :src="muestra.imagen"
            alt="Muestra"
          />
        </div>

        <div v-if="imagenes.length === 0" class="empty-gallery">
          Galería vacía
        </div>
      </div>

      <!-- VISOR -->
      <div class="viewer-column">

        <!-- TARJETA PRINCIPAL -->
        <div class="card main-card">
          <div class="card-header">
            <h3>
              {{ imagenSeleccionada ? 'Muestra ' + imagenSeleccionada.id_muestra : 'Sin imagen seleccionada' }}
            </h3>
            <div class="card-tools">
              <button class="tool-btn">✏️</button>
              <button class="tool-btn">🧹</button>
              <button class="tool-btn">🗑️</button>
              <button class="tool-btn">✔️</button>
            </div>
          </div>

          <div class="card-body split-view">

            <!-- IMAGEN -->
            <div class="image-container">
              <div class="img-placeholder">
                <img
                  v-if="imagenSeleccionada"
                  :src="imagenSeleccionada.imagen"
                  class="main-image"
                  style="width:100%; height:100%; object-fit:contain;"
                />
                <p
                  v-else
                  style="color:#999; text-align:center; margin-top:120px;"
                >
                  [Área de Imagen]
                </p>

                <div class="img-overlay">
                  <span class="overlay-badge left">Original</span>
                  <span class="overlay-badge right">Segmentación</span>
                </div>
              </div>
            </div>

            <!-- DATOS -->
            <div class="data-container">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>Estructura</th>
                    <th>Conteo</th>
                  </tr>
                </thead>

                <tbody v-if="resultadoImagenSeleccionada">
                  <tr>
                    <td>Núcleos</td>
                    <td>{{ resultadoImagenSeleccionada.nucleos }}</td>
                  </tr>
                  <tr>
                    <td>Membranas</td>
                    <td>{{ resultadoImagenSeleccionada.membranas }}</td>
                  </tr>
                  <tr class="row-highlight">
                    <td>Micronúcleos</td>
                    <td>{{ resultadoImagenSeleccionada.micronucleos }}</td>
                  </tr>
                </tbody>

                <tbody v-else>
                  <tr>
                    <td colspan="2" style="text-align:center; color:#999;">
                      Sin resultados disponibles
                    </td>
                  </tr>
                </tbody>
              </table>

              <button class="btn-outline full-width mt-auto">
                Marcar imagen para revisión manual
              </button>
            </div>

          </div>
        </div>

        <!-- TARJETA OBJETOS -->
        <div class="card objects-card">
          <div class="objects-layout">

            <div class="objects-table-wrapper">
              <table class="obj-table">
                <thead>
                  <tr>
                    <th>Ver</th>
                    <th>Tipo</th>
                    <th>Estado</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td><input type="checkbox" /></td>
                    <td>Núcleos</td>
                    <td>✏️ 🧹</td>
                  </tr>
                  <tr>
                    <td><input type="checkbox" /></td>
                    <td>Micronucleos</td>
                    <td>✏️ 🧹</td>
                  </tr>
                  <tr>
                    <td><input type="checkbox" /></td>
                    <td>Membranas</td>
                    <td>✏️ 🧹</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div class="objects-tools-panel">
              <div class="info-box">
                <p>Seleccione un objeto para editar.</p>
              </div>
              <button class="btn-tool-large">✏️ Marcar revisión</button>
              <button class="btn-tool-large">⬆ Exportar Datos</button>
            </div>

          </div>
        </div>

      </div>
    </div>
  </main>
</template>

<script>
import axios from "axios";

export default {
  name: "MainContent",

  props: {
    patientId: String,
    caseId: String,
  },

  data() {
    return {
      API_URL: "http://127.0.0.1:8000",

      analisis: [],
      loading: true,

      imagenSeleccionada: null,
    };
  },

  computed: {
    // Análisis según paciente y caso
    analisisActual() {
      if (!this.patientId || !this.caseId) return null;

      return this.analisis.find(
        a =>
          String(a.id_paciente_fk) === String(this.patientId) &&
          String(a.id_caso_fk) === String(this.caseId)
      );
    },

    // Muestras (imágenes)
    imagenes() {
      return this.analisisActual?.muestras_saliva || [];
    },

    // Resultado de la imagen seleccionada
    resultadoImagenSeleccionada() {
      if (!this.imagenSeleccionada) return null;
      return this.imagenSeleccionada.resultados?.[0] || null;
    },
  },

  watch: {
    // Selecciona la primera imagen automáticamente
    imagenes(nuevas) {
      this.imagenSeleccionada = nuevas[0] || null;
    },
  },

  mounted() {
    axios
      .get(`${this.API_URL}/api/analisis/`)
      .then((response) => {
        this.analisis = response.data;
      })
      .catch((error) => {
        console.error("Error API:", error);
      })
      .finally(() => {
        this.loading = false;
      });
  },
};
</script>

<style scoped>
.muted {
  color: #999;
  font-size: 14px;
}
/* Estilo base de la miniatura */
.thumb {
  cursor: pointer;
  border: 3px solid transparent;
  border-radius: 6px;
  transition: all 0.2s ease;
  opacity: 0.7;
  margin-bottom: 8px;
}

/* Estilo para cuando el mouse pasa por encima */
.thumb:hover {
  opacity: 1;
}

/* Estilo CUANDO ESTÁ SELECCIONADA (Clase .active) */
.thumb.active {
  border-color: #3b82f6;
  opacity: 1;
  box-shadow: 0 0 8px rgba(59, 130, 246, 0.5);
  transform: scale(1.02);
}

/* Asegurar que la imagen respete el contenedor */
.thumb img {
  width: 100%;
  height: auto;
  display: block;
  border-radius: 4px;
}
</style>

