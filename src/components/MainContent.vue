<template>
  <main class="content">

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

        <div class="gallery-column">
    <div
        v-for="img in imagenes"
        :key="img"
        class="thumb"
        :class="{ active: img === imagenSeleccionada }"
        @click="imagenSeleccionada = img"
    >
        <img
            v-if="patientId && caseId"
            :src="`/images/${patientId}/${caseId}/${img}`"
            alt=""
        />
    </div>

    <div v-if="imagenes.length === 0" class="empty-gallery">
        Galeria
    </div>
    </div>

      <div class="viewer-column">

        <!-- TARJETA PRINCIPAL -->
        <div class="card main-card">
          <div class="card-header">
            <h3>{{ imagenSeleccionada || "Sin imagen seleccionada" }}</h3>
            <div class="card-tools">
              <button class="tool-btn">✏️</button>
              <button class="tool-btn">🧹</button>
              <button class="tool-btn">🗑️</button>
              <button class="tool-btn">✔️</button>
            </div>
          </div>

          <div class="card-body split-view">

            <div class="image-container">
                <div class="img-placeholder">
                    <img
                    v-if="imagenActivaUrl"
                    :src="imagenActivaUrl"
                    class="main-image"
                    alt="Imagen seleccionada"
                    style="width:100%; height:100%; object-fit:contain;"
                    />
                    <p
                    v-else
                    style="color:#999; text-align:center; margin-top:120px;"
                    >
                    [Área de Imagen / Canvas]
                    </p>

                    <div class="img-overlay">
                    <span class="overlay-badge left">Original</span>
                    <span class="overlay-badge right">Segmentación</span>
                    </div>
                </div>
            </div>

            <div class="data-container">
              <table class="data-table">
                <thead>
                  <tr><th>Estructura</th><th>Conteo</th></tr>
                </thead>
                <tbody v-if="resultadoImagenSeleccionada">
                <tr>
                  <td>Núcleos</td>
                  <td>{{ resultadoImagenSeleccionada.Nucleos }}</td>
                </tr>
                <tr>
                  <td>Membranas</td>
                  <td>{{ resultadoImagenSeleccionada.Membranas }}</td>
                </tr>
                <tr class="row-highlight">
                  <td>Micronúcleos</td>
                  <td>{{ resultadoImagenSeleccionada.Micronucleos }}</td>
                </tr>
                <tr>
                  <td>Binucleadas</td>
                  <td>{{ resultadoImagenSeleccionada.Binucleadas }}</td>
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
                    <th></th>
                    <th>ID</th>
                    <th>Tipo</th>
                    <th>Estado</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td><input type="checkbox" /></td>
                    <td>N-1</td>
                    <td>Núcleo</td>
                    <td>✏️ 🧹</td>
                  </tr>
                  <tr>
                    <td><input type="checkbox" /></td>
                    <td>N-2</td>
                    <td>Núcleo</td>
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
export default {
  name: "MainContent",
  props: {
    patientId: {
      type: String,
      default: null,
    },
    caseId: {
      type: String,
      default: null,
    },
  },
  data() {
    return {
      imagenSeleccionada: null,

      imagenesPorCaso: {
        "P-1024": {
          "Caso-2023-A": [
            "01.jpg",
            "02.jpg",
            "03.jpg",
            "04.jpg",
            "05.jpg",
            "06.jpg",
            "07.jpg",
            "08.jpg",
            "09.jpg",
            "10.jpg",
            "11.jpg",
            "12.jpg",
            "13.jpg",
            "14.jpg",
            "15.jpg",
            "16.jpg",
            "17.jpg",
            "18.jpg",
            "19.jpg",
          ],
          "Caso-2024-B": [
            "10.jpg",
            "img_011.jpg",
          ],
        },
        "P-2001": {
          "Caso-2022-X": [
            "img_100.jpg",
            "img_101.jpg",
          ],
        },
      },

      // ✅ FUERA y al mismo nivel
      resultadosPorImagen: {
        "01.jpg": {
          Nucleos: 8,
          Membranas: 7,
          Micronucleos: 2,
          Binucleadas: "SI",
        },
        "02.jpg": {
          Nucleos: 10,
          Membranas: 6,
          Micronucleos: 1,
          Binucleadas: "NO",
        },
        "03.jpg": {
          Nucleos: 6,
          Membranas: 5,
          Micronucleos: 0,
          Binucleadas: "NO",
        },
      },
    };
  },
  computed: {
    // Devuelve las imágenes según paciente y caso
    imagenes() {
      if (!this.patientId || !this.caseId) return [];
      return (
        this.imagenesPorCaso[this.patientId]?.[this.caseId] || []
      );
    },
    // URL de la imagen activa
    imagenActivaUrl() {
      if (!this.imagenSeleccionada) return null;
      return `/images/${this.patientId}/${this.caseId}/${this.imagenSeleccionada}`;
    },
    resultadoImagenSeleccionada() {
      if (!this.imagenSeleccionada) return null;
      return this.resultadosPorImagen[this.imagenSeleccionada] || null;
    },
  },
  methods: {
    limpiarVista() {
      this.imagenSeleccionada = null;
    },
  },
  watch: {
  // Cuando cambian las imágenes (paciente o caso)
    imagenes(nuevas) {
    if (!this.patientId || !this.caseId) {
      this.imagenSeleccionada = null;
      return;
    }
    this.imagenSeleccionada = nuevas[0] || null;
  },

    // 👉 Si se borra o cambia el paciente
    patientId(nuevo) {
      if (!nuevo) {
        this.limpiarVista();
      }
    },

    // 👉 Si se borra o cambia el caso
    caseId(nuevo) {
      if (!nuevo) {
        this.limpiarVista();
      }
    },
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
