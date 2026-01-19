<template>
  <!-- BARRA SUPERIOR -->
  <TopBar
    :seccion="seccion"
    @change-section="seccion = $event"
  />

  <!-- CONTENIDO PRINCIPAL -->
  <div v-if="seccion !== 'dev'" class="app">

    <!-- SIDEBAR -->
    <SideBar
      v-if="seccion === 'analisis'"
      @select-patient="onSelectPatient"
      @select-case="onSelectCase"
    />

    <!-- CONTENIDO CENTRAL -->
    <MainContent
      v-if="seccion === 'analisis'"
      :patientId="selectedPatientId"
      :caseId="selectedCaseId"
    />

    <div v-if="seccion === 'segmentacion'">
      Segmentacion
    </div>

    <!-- PLACEHOLDERS FUTUROS -->
    <div v-if="seccion === 'caracterizacion'">
      Caracterización
    </div>

  </div>

  <!-- VISTA DESARROLLO   (BORRAR DESPUES)  -->
  <CargaAnalisis v-if="seccion === 'dev'" />

</template>

<script>
import TopBar from "./components/TopBar.vue";
import SideBar from "./components/SideBar.vue";
import MainContent from "./components/MainContent.vue";
import CargaAnalisis from "./views/CargaAnalisis.vue";

export default {
  name: "App",

  components: {
    TopBar,
    SideBar,
    MainContent,
    CargaAnalisis,
  },

  data() {
    return {
      // Sección activa
      seccion: "analisis",

      // Estado global de selección
      selectedPatientId: null,
      selectedCaseId: null,
    };
  },

  methods: {
    // Recibe paciente desde SideBar
    onSelectPatient(patientId) {
      this.selectedPatientId = patientId;
      this.selectedCaseId = null; // resetear caso
    },

    // Recibe caso desde SideBar
    onSelectCase(caseId) {
      this.selectedCaseId = caseId;
    },
  },

  watch: {
    // Limpieza de estado al cambiar de sección
    seccion(nueva) {
      if (nueva !== "analisis") {
        this.selectedPatientId = null;
        this.selectedCaseId = null;
      }
    },
  },
};
</script>

<style>
/* =========================================
   CONFIGURACIÓN BASE
   ========================================= */
* {
    box-sizing: border-box;
    font-family: system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif;
}

body {
    margin: 0;
    background: #f4f6f9;
    color: #333;
    height: 100vh;
    overflow: hidden;
}

/* =========================================
   TOPBAR
   ========================================= */
.topbar {
    height: 50px;
    background: #ffffff;
    border-bottom: 1px solid #ddd;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 20px;
}

.logo {
    font-weight: 600;
    font-size: 16px;
}

.nav-buttons .nav-btn {
    margin-left: 20px;
    font-size: 14px;
    color: #666;
    text-decoration: none;
    cursor: pointer;
}

/* =========================================
   LAYOUT GENERAL
   ========================================= */
.app {
    display: flex;
    height: calc(100vh - 50px);
}

/* =========================================
   SIDEBAR
   ========================================= */
.sidebar {
    width: 260px;
    background: #ffffff;
    border-right: 1px solid #ddd;
    padding: 15px;
    display: flex;
    flex-direction: column;
    overflow-y: auto;
}

.sidebar h2 {
    font-size: 15px;
    margin-bottom: 15px;
}

.form-group {
    margin-bottom: 12px;
}

.form-group label {
    font-size: 12px;
    color: #666;
    margin-bottom: 4px;
    display: block;
}

.form-group input,
.form-group select {
    width: 100%;
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 4px;
}

.btn-primary {
    margin-top: 10px;
    padding: 10px;
    border: 1px solid #ccc;
    background: #fff;
    cursor: pointer;
}

/* Resumen */
.summary-panel {
    margin-top: 20px;
    padding-top: 15px;
    border-top: 1px solid #eee;
}

.summary-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
}

.summary-grid div {
    border: 1px solid #ddd;
    border-radius: 6px;
    padding: 10px;
    text-align: center;
}

.summary-grid b {
    display: block;
    font-size: 18px;
}

.summary-grid span {
    font-size: 11px;
    color: #777;
}

/* =========================================
   CONTENIDO
   ========================================= */
.content {
    flex: 1;
    padding: 15px 20px;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

.page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
}

.btn-outline {
    padding: 6px 12px;
    border: 1px solid #ccc;
    background: #fff;
    cursor: pointer;
    font-size: 13px;
}

/* =========================================
   GRID PRINCIPAL
   ========================================= */
.layout-grid {
    display: flex;
    gap: 15px;
    height: 100%;
    overflow: hidden;
}

/* =========================================
   GALERÍA
   ========================================= */
.gallery-column {
    width: 210px;
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    grid-auto-rows: 65px;
    gap: 8px;
    overflow-y: auto;
}

.thumb {
    background: #e0e0e0;
    border: 1px solid #ccc;
    border-radius: 4px;
}

/* =========================================
   VISOR
   ========================================= */
.viewer-column {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 15px;
    overflow-y: auto;
}

/* Tarjetas */
.card {
    background: #ffffff;
    border: 1px solid #ddd;
    border-radius: 8px;
    display: flex;
    flex-direction: column;
}

.card-header {
    padding: 10px 15px;
    border-bottom: 1px solid #ddd;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.card-header h3 {
    font-size: 14px;
    margin: 0;
}

/* Herramientas */
.card-tools {
    display: flex;
    gap: 6px;
}

.tool-btn {
    width: 30px;
    height: 30px;
    border: 1px solid #ccc;
    background: #fff;
    cursor: pointer;
}

/* =========================================
   VISTA DIVIDIDA
   ========================================= */
.split-view {
    display: flex;
    gap: 20px;
    padding: 15px;
    height: 380px;
}

.image-container {
    flex: 1.6;
    display: flex;
    flex-direction: column;
}

.img-placeholder {
    position: relative;
    flex: 1;
    background: #e0e0e0;
    border: 1px solid #ccc;
    border-radius: 6px;
    overflow: hidden;
}

.img-overlay {
    position: absolute;
    bottom: 8px;
    left: 0;
    right: 0;
    display: flex;
    justify-content: space-between;
    padding: 0 10px;
    pointer-events: none;
}

/* Badges */
.overlay-badge {
    font-size: 11px;
    padding: 4px 8px;
    border-radius: 4px;
    background: rgba(0,0,0,0.65);
    color: #fff;
}

.img-controls {
    display: flex;
    justify-content: space-between;
    margin-top: 8px;
}

.badge {
    font-size: 11px;
    padding: 4px 8px;
    border: 1px solid #ccc;
}

/* Datos */
.data-container {
    flex: 1;
    display: flex;
    flex-direction: column;
}

.data-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
}

.data-table th,
.data-table td {
    padding: 8px;
    border: 1px solid #ddd;
}

.full-width {
    width: 100%;
}

.mt-auto {
    margin-top: auto;
}

/* =========================================
   OBJETOS
   ========================================= */
.objects-card {
    flex: 1;
    min-height: 200px;
}

.objects-layout {
    display: flex;
    height: 100%;
}

.objects-table-wrapper {
    flex: 1;
    padding: 15px;
    border-right: 1px solid #ddd;
    overflow-y: auto;
}

.obj-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
}

.obj-table th,
.obj-table td {
    padding: 10px;
    border-bottom: 1px solid #ddd;
}

.objects-tools-panel {
    width: 240px;
    padding: 15px;
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.info-box {
    border: 1px solid #ddd;
    padding: 10px;
    font-size: 12px;
}

.btn-tool-large {
    padding: 12px;
    border: 1px solid #ccc;
    background: #fff;
    cursor: pointer;
}
</style>
