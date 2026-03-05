<template>
  <!-- BARRA SUPERIOR -->
  <TopBar
    :seccion="seccion"
    :caseId="selectedCaseId"
    @change-section="seccion = $event"
    @toggle-sidebar="sidebarOpen = !sidebarOpen"
  />

  <div
    v-show="sidebarOpen && seccion === 'segmentacion'"
    class="sidebar-overlay"
    @click="sidebarOpen = false"
  ></div>

  <!-- ===== LAYOUT CON SIDEBAR (SEGMENTACIÓN) ===== -->
  <div class="app" v-show="seccion === 'segmentacion'">
    <SideBar
      ref="sidebar"
      :isOpen="sidebarOpen"
      @close-sidebar="sidebarOpen = false"
      @select-patient="onSelectPatient"
      @select-case="onSelectCase"
      @reset-selection="resetSelection"
    />
    <MainContent
      :patientId="selectedPatientId"
      :caseId="selectedCaseId"
      @edicion-guardada="$refs.sidebar.recargarResumen()"
    />
  </div>

  <div class="app-single" v-show="seccion === 'caracterizacion'">
    <CaracterizacionView
      :patientId="selectedPatientId"
      :caseId="selectedCaseId"
      @update-patient="onSelectPatient"
      @update-case="onSelectCase"
      @go-segmentacion="seccion = 'segmentacion'"
    />
  </div>

  <!-- ===== REGISTRO — necesita scroll propio ===== -->
  <div class="app-single app-registro" v-show="seccion === 'registro'">
    <RegistroView />
  </div>
</template>

<script>
import TopBar from "./components/TopBar.vue";
import SideBar from "./components/SideBar.vue";
import MainContent from "./components/MainContent.vue";
import RegistroView from "./views/RegistroView.vue";
import CaracterizacionView from "./views/CaracterizacionView.vue";

export default {
  name: "App",
  components: { TopBar, SideBar, MainContent, RegistroView, CaracterizacionView },

  data() {
    return {
      seccion: "segmentacion",
      selectedPatientId: null,
      selectedCaseId: null,
      sidebarOpen: false,
    };
  },

  methods: {
    onSelectPatient(patientId) {
      this.selectedPatientId = patientId;
      this.selectedCaseId = null;
    },
    onSelectCase(caseId) {
      this.selectedCaseId = caseId;
    },
    resetSelection() {
      this.selectedPatientId = null;
      this.selectedCaseId = null;
    },
  },

  watch: {
    seccion(nueva) {
      if (nueva !== "segmentacion") {
        this.sidebarOpen = false;
      } else {
        this.sidebarOpen = true;
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
  font-family:
    -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

body {
  margin: 0;
  background: #f0f2f5;
  color: #2c3e50;
  height: 100vh;
  /*  FIX: overflow:hidden solo cuando NO estamos en registro.
     Lo manejamos por sección con clases específicas. */
  overflow: hidden;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* =========================================
   LAYOUT GENERAL
========================================= */
.app {
  display: flex;
  height: calc(100vh - 60px);
  background: #f0f2f5;
  overflow: hidden; /* segmentación no necesita scroll en el body */
}

/* Vista simple (sin sidebar) */
.app-single {
  height: calc(100vh - 60px);
  overflow: hidden; /* placeholder views no necesitan scroll */
}

/* ✅ FIX PRINCIPAL: Registro necesita scroll vertical propio */
.app-registro {
  overflow-y: auto !important;
  overflow-x: hidden;
}

/* =========================================
   PLACEHOLDER VIEWS
========================================= */
.placeholder-view {
  flex: 1;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 40px;
}

.placeholder-content {
  text-align: center;
  background: white;
  padding: 60px 80px;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  max-width: 500px;
  animation: fadeInUp 0.6s ease;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.placeholder-icon {
  font-size: 80px;
  margin-bottom: 20px;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

.placeholder-content h2 {
  margin: 0 0 12px 0;
  font-size: 32px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.placeholder-content p {
  margin: 0 0 24px 0;
  color: #666;
  font-size: 16px;
  line-height: 1.6;
}

.placeholder-badge {
  display: inline-block;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 10px 24px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 0.5px;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

/* =========================================
   SCROLLBAR PERSONALIZADA
========================================= */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}
::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 10px;
}
::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
}
::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
}

/* =========================================
   UTILIDADES GLOBALES
========================================= */
.text-center {
  text-align: center;
}
.mt-auto {
  margin-top: auto;
}
.full-width {
  width: 100%;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
.loading {
  animation: pulse 1.5s ease-in-out infinite;
}

.skeleton {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s ease-in-out infinite;
}
@keyframes loading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

*:focus-visible {
  outline: 3px solid #667eea;
  outline-offset: 2px;
}

::selection {
  background: #667eea;
  color: white;
}
::-moz-selection {
  background: #667eea;
  color: white;
}

/* =========================================
   RESPONSIVE
========================================= */
@media (max-width: 1200px) {
  .app {
    position: relative;
  }
}

.sidebar-overlay {
  display: none;
}

@media (max-width: 1200px) {
  .sidebar-overlay {
    display: block;
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.35);
    z-index: 900;
  }
}
</style>
