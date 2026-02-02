<template>
  <main class="content">

    <!-- HEADER -->
    <header class="page-header">
      <div class="header-left">
        <h2 class="page-title">
          Resultados del Análisis
        </h2>
        <div class="breadcrumb">
          <span v-if="patientId" class="breadcrumb-item">
            👤 Paciente {{ patientId }}
          </span>
          <span v-if="caseId" class="breadcrumb-separator">›</span>
          <span v-if="caseId" class="breadcrumb-item active">
            📋 Caso {{ caseId }}
          </span>
          <span v-if="!patientId" class="breadcrumb-placeholder">
            Seleccione un paciente y un caso para comenzar
          </span>
        </div>
      </div>

      <div class="header-actions">
        <button class="btn-action csv">
          <span class="btn-icon">⬇</span>
          Exportar CSV
        </button>
        <button class="btn-action pdf">
          <span class="btn-icon">📄</span>
          Generar PDF
        </button>
      </div>
    </header>

    <div class="layout-grid">

      <!-- GALERÍA -->
      <div class="gallery-column">
        <div class="gallery-header">
          <h3>Galería</h3>
          <span class="gallery-count">{{ imagenes.length }}</span>
        </div>

        <div class="gallery-grid">
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
            <div class="thumb-overlay">
              <span class="thumb-id">#{{ muestra.id_muestra }}</span>
            </div>
          </div>

          <div v-if="imagenes.length === 0" class="empty-gallery">
            <div class="empty-icon">🖼️</div>
            <p>No hay imágenes disponibles</p>
            <span>Seleccione un caso válido</span>
          </div>
        </div>
      </div>

      <!-- VISOR -->
      <div class="viewer-column">

        <!-- TARJETA PRINCIPAL -->
        <div class="card main-card">
          
          <div class="card-body split-view">

            <!-- IMAGEN -->
            <div class="image-container">
              <div class="img-placeholder">
                <img
                  v-if="imagenSeleccionada"
                  :src="imagenSeleccionada.imagen"
                  class="main-image clickable"
                  alt="Muestra microscópica"
                  @click="imagenEnEdicion = true"
                />
                <div
                  v-else
                  class="empty-image-state"
                >
                  <div class="empty-image-icon">🔬</div>
                  <p>Seleccione una imagen de la galería</p>
                </div>

                <div v-if="imagenSeleccionada" class="img-overlay">
                  <span class="overlay-badge original">Original</span>
                  <span class="overlay-badge segmented">Segmentación</span>
                </div>
              </div>
            </div>

            <!-- DATOS -->
            <div class="data-container">

              <div class="card-header">

                <div class="card-title-section">
                  <h3>
                    {{ imagenSeleccionada ? 'Muestra #' + imagenSeleccionada.id_muestra : 'Vista previa' }}
                  </h3>

                </div>

                <div class="card-tools">

                  <button class="tool-btn" title="Editar">
                    <span>✏️</span>
                  </button>
                  <button class="tool-btn" title="Limpiar">
                    <span>🧹</span>
                  </button>
                  <button class="tool-btn danger" title="Eliminar">
                    <span>🗑️</span>
                  </button>
                  <button class="tool-btn success" title="Aprobar">
                    <span>✔️</span>
                  </button>

                </div>
              
              </div>

              <div class="data-header">
                <h4>Resumen de Conteo</h4>
              </div>
              
              <table class="data-table">
                <thead>
                  <tr>
                    <th>Estructura</th>
                    <th>Cantidad</th>
                  </tr>
                </thead>

                <tbody v-if="resultadoImagenSeleccionada">
                  <tr class="data-row nucleos">
                    <td>
                      <span class="structure-icon">🟢</span>
                      Núcleos
                    </td>
                    <td class="count">{{ resultadoImagenSeleccionada.nucleos }}</td>
                  </tr>
                  <tr class="data-row membranas">
                    <td>
                      <span class="structure-icon">🟤</span>
                      Membranas
                    </td>
                    <td class="count">{{ resultadoImagenSeleccionada.membranas }}</td>
                  </tr>
                  <tr class="data-row micronucleos highlight">
                    <td>
                      <span class="structure-icon">🔴</span>
                      Micronúcleos
                    </td>
                    <td class="count critical">{{ resultadoImagenSeleccionada.micronucleos }}</td>
                  </tr>
                </tbody>

                <tbody v-else>
                  <tr>
                    <td colspan="2" class="no-data">
                      <div class="no-data-icon">📊</div>
                      <span>Sin resultados disponibles</span>
                    </td>
                  </tr>
                </tbody>
              </table>
              
              <button class="btn-review full-width">
                <span class="btn-icon">⚠️</span>
                Marcar para revisión manual
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
                    <th>Visible</th>
                    <th>Tipo de Objeto</th>
                    <th>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  <tr class="obj-row">
                    <td>
                      <input type="checkbox" class="checkbox-custom" checked />
                    </td>
                    <td class="obj-type">
                      <span class="obj-icon nucleos">●</span>
                      Núcleos
                    </td>
                    <td>
                      <div class="obj-actions">
                        <button class="obj-btn" title="Editar">✏️</button>
                        <button class="obj-btn" title="Limpiar">🧹</button>
                      </div>
                    </td>
                  </tr>
                  <tr class="obj-row">
                    <td>
                      <input type="checkbox" class="checkbox-custom" checked />
                    </td>
                    <td class="obj-type">
                      <span class="obj-icon micronucleos">●</span>
                      Micronúcleos
                    </td>
                    <td>
                      <div class="obj-actions">
                        <button class="obj-btn" title="Editar">✏️</button>
                        <button class="obj-btn" title="Limpiar">🧹</button>
                      </div>
                    </td>
                  </tr>
                  <tr class="obj-row">
                    <td>
                      <input type="checkbox" class="checkbox-custom" checked />
                    </td>
                    <td class="obj-type">
                      <span class="obj-icon membranas">●</span>
                      Membranas
                    </td>
                    <td>
                      <div class="obj-actions">
                        <button class="obj-btn" title="Editar">✏️</button>
                        <button class="obj-btn" title="Limpiar">🧹</button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </main>

<!-- OVERLAY EDICIÓN IMAGEN -->
<div
  v-if="imagenEnEdicion"
  class="image-editor-overlay"
  @click.self="imagenEnEdicion = false"
>

  <!-- FLECHA IZQUIERDA -->
  <button
    class="nav-arrow left"
    @click.stop="imagenAnterior"
    :disabled="indiceImagenSeleccionada <= 0"
  >
    ‹
  </button>

  <div class="editor-container">
    <button class="close-btn" @click="imagenEnEdicion = false">✖</button>

    <div
      class="editor-image-wrapper"
      @wheel.prevent="onWheelZoom"

      @mousedown="startDrag"
      @mousemove="onDrag"
      @mouseup="endDrag"
      @mouseleave="endDrag"
    >
      <img
        :src="imagenSeleccionada.imagen"
        class="editor-image"
        alt="Imagen en edición"
        @dblclick.stop="resetZoom"
        :style="{
          transform: `translate(${offsetX}px, ${offsetY}px) scale(${zoom})`,
          cursor: zoom > 1
            ? (isDragging ? 'grabbing' : 'grab')
            : 'zoom-in'
        }"
      />
    </div>

    <!-- FLECHA DERECHA -->
  <button
    class="nav-arrow right"
    @click.stop="siguienteImagen"
    :disabled="indiceImagenSeleccionada >= imagenes.length - 1"
  >
    ›
  </button>

    <!-- Aquí luego puedes meter herramientas -->
    <div class="editor-tools">
      <button>✏️ Editar</button>
    </div>
  </div>
</div>

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
      imagenEnEdicion: false,
      // ZOOM
      zoom: 1,
      zoomMin: 1,
      zoomMax: 4,
      zoomStep: 0.15,
      offsetX: 0,
      offsetY: 0,
      //Mover Imagen
      isDragging: false,
      startX: 0,
      startY: 0,
    };
  },

  computed: {
    analisisActual() {
      if (!this.patientId || !this.caseId) return null;

      return this.analisis.find(
        a =>
          String(a.id_paciente_fk) === String(this.patientId) &&
          String(a.id_caso_fk) === String(this.caseId)
      );
    },

    imagenes() {
      return this.analisisActual?.muestras_saliva || [];
    },

    resultadoImagenSeleccionada() {
      if (!this.imagenSeleccionada) return null;
      return this.imagenSeleccionada.resultados?.[0] || null;
    },

    indiceImagenSeleccionada() {
      if (!this.imagenSeleccionada) return -1;
      return this.imagenes.findIndex(
        img => img.id_muestra === this.imagenSeleccionada.id_muestra
      );
    },
  },

  watch: {
    imagenes(nuevas) {
      this.imagenSeleccionada = nuevas[0] || null;
    },

    imagenSeleccionada() {
      this.zoom = 1;
      this.offsetX = 0;
      this.offsetY = 0;
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

      window.addEventListener("keydown", this.teclasOverlay);
  },

  beforeUnmount() {
    window.removeEventListener("keydown", this.teclasOverlay);
  },

  methods: {
    siguienteImagen() {
      if (this.indiceImagenSeleccionada < this.imagenes.length - 1) {
        this.imagenSeleccionada =
          this.imagenes[this.indiceImagenSeleccionada + 1];
      }
    },
    imagenAnterior() {
      if (this.indiceImagenSeleccionada > 0) {
        this.imagenSeleccionada =
          this.imagenes[this.indiceImagenSeleccionada - 1];
      }
    },
    teclasOverlay(e) {
      if (!this.imagenEnEdicion) return;

      if (e.key === "ArrowRight") this.siguienteImagen();
      if (e.key === "ArrowLeft") this.imagenAnterior();
      if (e.key === "Escape") this.imagenEnEdicion = false;
    },
    onWheelZoom(e) {
      const zoomAnterior = this.zoom;

      // 1. Calcular nuevo zoom
      if (e.deltaY < 0 && this.zoom < this.zoomMax) {
        this.zoom += this.zoomStep;
      }
      if (e.deltaY > 0 && this.zoom > this.zoomMin) {
        this.zoom -= this.zoomStep;
      }

      // Si no cambió el zoom, salir
      if (this.zoom === zoomAnterior) return;

      // 2. Posición del mouse dentro del contenedor
      const rect = e.currentTarget.getBoundingClientRect();
      const mouseX = e.clientX - rect.left;
      const mouseY = e.clientY - rect.top;

      // 3. Centro del contenedor
      const centerX = rect.width / 2;
      const centerY = rect.height / 2;

      // 4. Distancia del mouse al centro
      const dx = mouseX - centerX;
      const dy = mouseY - centerY;

      // 5. Ajuste por cambio de escala
      const factor = this.zoom / zoomAnterior;

      this.offsetX -= dx * (factor - 1);
      this.offsetY -= dy * (factor - 1);

      // 6. Reset cuando vuelve a zoom normal
      if (this.zoom === 1) {
        this.offsetX = 0;
        this.offsetY = 0;
      }
    },
    resetZoom() {
      this.zoom = 1;
      this.offsetX = 0;
      this.offsetY = 0;
    },
    startDrag(e) {
      if (this.zoom <= 1) return;

      this.isDragging = true;
      this.startX = e.clientX - this.offsetX;
      this.startY = e.clientY - this.offsetY;
    },

    onDrag(e) {
      if (!this.isDragging || this.zoom <= 1) return;

      this.offsetX = e.clientX - this.startX;
      this.offsetY = e.clientY - this.startY;
    },

    endDrag() {
      this.isDragging = false;
    },

  },

};

</script>

<style scoped>
.content {
  flex: 1;
  padding: 16px;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  background: #f8f9fa;
  height: 100vh;
}

/* HEADER */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 2px solid #e0e0e0;
  height: 60px;
}

.header-left {
  flex: 1;
}

.page-title {
  margin: 0 0 6px 0;
  font-size: 24px;
  font-weight: 700;
  color: #2c3e50;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.breadcrumb-item {
  color: #666;
  padding: 4px 10px;
  background: #f0f4f8;
  border-radius: 6px;
}

.breadcrumb-item.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-weight: 500;
}

.breadcrumb-separator {
  color: #999;
}

.breadcrumb-placeholder {
  color: #999;
  font-style: italic;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.btn-action {
  padding: 10px 18px;
  border: 2px solid #e0e0e0;
  background: white;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  border-radius: 10px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #2c3e50;
}

.btn-action:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.btn-action.csv:hover {
  border-color: #43a047;
  background: #e8f5e9;
}

.btn-action.pdf:hover {
  border-color: #e53935;
  background: #ffebee;
}

.btn-icon {
  font-size: 16px;
}

/* LAYOUT */
.layout-grid {
  display: flex;
  gap: 16px;
  height: auto;
  min-height: 0;
  overflow: visible;
}

/* GALERÍA */
.gallery-column {
  width: 200px;;
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 12px;
  padding: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.gallery-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 10px;
  border-bottom: 2px solid #f0f0f0;
}

.gallery-header h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #2c3e50;
}

.gallery-count {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
}

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  grid-auto-rows: 60px;
  gap: 8px;
  overflow-y: auto;
}

.thumb {
  cursor: pointer;
  border: 3px solid transparent;
  border-radius: 10px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  opacity: 0.7;
  overflow: hidden;
  position: relative;
  background: #f0f0f0;
}

.thumb:hover {
  opacity: 1;
  transform: scale(1.05);
}

.thumb.active {
  border-color: #667eea;
  opacity: 1;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.4);
  transform: scale(1.05);
}

.thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.thumb-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(to top, rgba(0,0,0,0.7), transparent);
  padding: 4px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.thumb:hover .thumb-overlay,
.thumb.active .thumb-overlay {
  opacity: 1;
}

.thumb-id {
  color: white;
  font-size: 10px;
  font-weight: 600;
}

.empty-gallery {
  grid-column: 1 / -1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px 20px;
  text-align: center;
  color: #999;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 12px;
  opacity: 0.3;
}

.empty-gallery p {
  margin: 0 0 4px 0;
  font-size: 14px;
  font-weight: 500;
  color: #666;
}

.empty-gallery span {
  font-size: 12px;
  color: #999;
}

/* VISOR */
.viewer-column {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
  height: auto;
  min-height: 700px;
  overflow: hidden;
}

/* TARJETAS */
.card {
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.main-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
}

.card-header {
  padding: 16px 20px;
  border-bottom: 2px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(to right, #fafbfc, #ffffff);
  flex-shrink: 0;
}

.card-title-section h3 {
  font-size: 16px;
  margin: 0 0 2px 0;
  font-weight: 600;
  color: #2c3e50;
}

.card-subtitle {
  font-size: 12px;
  color: #999;
}

.card-tools {
  display: flex;
  gap: 8px;
}

.tool-btn {
  width: 36px;
  height: 36px;
  border: 2px solid #e0e0e0;
  background: white;
  cursor: pointer;
  border-radius: 8px;
  font-size: 16px;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tool-btn:hover {
  background: #f0f4f8;
  transform: translateY(-2px);
}

.tool-btn.danger:hover {
  border-color: #ef5350;
  background: #ffebee;
}

.tool-btn.success:hover {
  border-color: #66bb6a;
  background: #e8f5e9;
}

/* VISTA DIVIDIDA */
.split-view {
  display: flex;
  gap: 20px;
  padding: 16px;
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

.image-container {
  flex: 1.6;
  display: flex;
  flex-direction: column;
  gap: 10px;
  height: 100%;
  min-height: 0;
}

.img-placeholder {
  position: relative;
  flex: 1;
  background: #f8f9fa;
  border: 2px dashed #e0e0e0;
  border-radius: 12px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  position: relative;
  min-height: 0px;
}

.main-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
}

.empty-image-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: #999;
}

.empty-image-icon {
  font-size: 64px;
  opacity: 0.3;
}

.empty-image-state p {
  margin: 0;
  font-size: 14px;
}

.img-overlay {
  position: absolute;
  bottom: 12px;
  left: 12px;
  right: 12px;
  display: flex;
  justify-content: space-between;
  gap: 8px;
}

.overlay-badge {
  font-size: 11px;
  padding: 6px 12px;
  border-radius: 8px;
  font-weight: 600;
  backdrop-filter: blur(10px);
}

.overlay-badge.original {
  background: rgba(66, 165, 245, 0.9);
  color: white;
}

.overlay-badge.segmented {
  background: rgba(255, 152, 0, 0.9);
  color: white;
}

/* DATOS */
.data-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.data-header {
  padding-bottom: 8px;
  border-bottom: 2px solid #f0f0f0;
}

.data-header h4 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #2c3e50;
}

.data-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  font-size: 13px;
}

.data-table thead th {
  padding: 12px;
  background: #f8f9fa;
  border-bottom: 2px solid #e0e0e0;
  text-align: left;
  font-weight: 600;
  color: #666;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.data-table tbody td {
  padding: 14px 12px;
  border-bottom: 1px solid #f0f0f0;
}

.data-row {
  transition: background 0.2s ease;
}

.data-row:hover {
  background: #f8f9fa;
}

.data-row.highlight {
  background: #fff3e0;
}

.data-row.highlight:hover {
  background: #ffe0b2;
}

.structure-icon {
  margin-right: 8px;
  font-size: 14px;
}

.count {
  font-weight: 700;
  font-size: 16px;
  text-align: right;
  color: #2c3e50;
}

.count.critical {
  color: #ef5350;
}

.no-data {
  text-align: center;
  padding: 40px 20px !important;
  color: #999;
}

.no-data-icon {
  font-size: 48px;
  margin-bottom: 12px;
  opacity: 0.3;
}

.btn-review {
  padding: 14px;
  border: 2px solid #ff9800;
  background: white;
  color: #f57c00;
  cursor: pointer;
  font-size: 13px;
  font-weight: 600;
  border-radius: 10px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: auto;
}

.btn-review:hover {
  background: #fff3e0;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 152, 0, 0.2);
}

.full-width {
  width: 100%;
}

/* OBJETOS */
.objects-card {
  height: 250px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
}

.card-header {
  padding: 8px 20px; /* Reducido para que sea más delgada */
  border-bottom: 2px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(to right, #fafbfc, #ffffff);
  flex-shrink: 0;
  height: 50px;
}

.card-header-simple {
  padding: 10px 20px;
  border-bottom: 2px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(to right, #fafbfc, #ffffff);
  flex-shrink: 0;
}

.card-header-simple h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
}

.objects-count {
  font-size: 12px;
  color: #999;
  background: #f0f4f8;
  padding: 4px 12px;
  border-radius: 12px;
}

.objects-layout {
  display: flex;
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

.objects-table-wrapper {
  flex: 1;
  padding: 16px;
  padding-bottom: 100px;
  border-right: 2px solid #f0f0f0;
  overflow-y: auto;
  min-height: 0;
}

.obj-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  font-size: 13px;
}

.obj-table thead th {
  padding: 12px;
  background: #f8f9fa;
  border-bottom: 2px solid #e0e0e0;
  text-align: center;
  font-weight: 600;
  color: #666;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.obj-table tbody td {
  padding: 12px;
  border-bottom: 1px solid #f0f0f0;
  text-align: center;
}

.obj-row {
  transition: background 0.2s ease;
}

.obj-row:hover {
  background: #f8f9fa;
}

.checkbox-custom {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: #667eea;
}

.obj-type {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-weight: 500;
}

.obj-icon {
  font-size: 16px;
}

.obj-icon.nucleos {
  color: #66bb6a;
}

.obj-icon.micronucleos {
  color: #ef5350;
}

.obj-icon.membranas {
  color: #8d6e63;
}

.obj-actions {
  display: flex;
  gap: 6px;
  justify-content: center;
}

.obj-btn {
  width: 32px;
  height: 32px;
  border: 2px solid #e0e0e0;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
}

.obj-btn:hover {
  background: #f0f4f8;
  border-color: #1e88e5;
  transform: scale(1.1);
}

/* OVERLAY EDICIÓN */
.image-editor-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.editor-container {
  position: relative;
  background: #fff;
  border-radius: 14px;
  padding: 20px;
  max-width: 90vw;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  gap: 14px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.4);
  animation: zoomIn 0.25s ease;
}

.editor-image {
  max-width: 85vw;
  max-height: 70vh;
  object-fit: contain;
  border-radius: 10px;
  background: #f5f5f5;
}

.editor-tools {
  display: flex;
  gap: 10px;
  justify-content: center;
}

.editor-tools button {
  padding: 10px 16px;
  border: 2px solid #e0e0e0;
  background: white;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s ease;
}

.editor-tools button:hover {
  border-color: #667eea;
  background: #eef1ff;
}

.close-btn {
  position: absolute;
  top: 12px;
  right: 12px;
  border: none;
  background: #ef5350;
  color: white;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 16px;
  z-index: 10;
}

.clickable {
  cursor: zoom-in;
}

/* ANIMACIÓN */
@keyframes zoomIn {
  from {
    transform: scale(0.9);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

/* Flechas */
.nav-arrow {
  position: fixed;
  top: 50%;
  transform: translateY(-50%);
  width: 54px;
  height: 54px;
  border-radius: 50%;
  border: none;
  background: rgba(0, 0, 0, 0.6);
  color: white;
  font-size: 32px;
  cursor: pointer;
  z-index: 10000;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.nav-arrow:hover {
  background: rgba(102, 126, 234, 0.9);
  transform: translateY(-50%) scale(1.1);
}

.nav-arrow.left {
  left: 24px;
}

.nav-arrow.right {
  right: 24px;
}

.nav-arrow:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.editor-image-wrapper {
  max-width: 85vw;
  max-height: 70vh;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
  border-radius: 12px;
}

@media (max-width: 1200px) {

  /* Galería más delgada */
  .gallery-column {
    width: 120px;   /* antes 230px */
    padding: 8px;
  }

  /* Galería en UNA sola columna */
  .gallery-grid {
    grid-template-columns: 1fr;
    grid-auto-rows: 70px;
  }

  /* Miniaturas más compactas */
  .thumb {
    border-width: 2px;
    border-radius: 8px;
  }

  .thumb-id {
    font-size: 9px;
  }

}
</style>
