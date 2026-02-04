<template>
  <aside class="sidebar" :class="{ open: isOpen }">
    <button class="close-btn" @click="$emit('close-sidebar')">✕</button>
    <h2>Búsqueda de Casos</h2>

    <!-- BUSCADOR DE PACIENTE -->
    <div class="search-section">
      <label>Buscar Paciente</label>
      <div class="search-input-wrapper">
        <input
          type="text"
          v-model="busquedaPaciente"
          placeholder="Nombre, apellido o ID..."
          @input="filtrarPacientes"
          @focus="mostrarDropdown = true"
        />
        <span class="search-icon">🔍</span>
      </div>

      <div v-if="mostrarDropdown && pacientesFiltrados.length > 0" class="pacientes-dropdown">
        <div
          v-for="paciente in pacientesFiltrados.slice(0, 5)"
          :key="paciente.id_paciente"
          class="paciente-item"
          @click="seleccionarPaciente(paciente)"
        >
          <div class="paciente-nombre">{{ paciente.nombre }} {{ paciente.apellido }}</div>
          <div class="paciente-meta">ID: {{ paciente.identificacion }}</div>
        </div>
      </div>
    </div>

    <!-- PACIENTE -->
    <div v-if="pacienteSeleccionado" class="paciente-card">
      <h3>
        {{ pacienteSeleccionado.nombre }}
        {{ pacienteSeleccionado.apellido }}
      </h3>
      <p>ID: {{ pacienteSeleccionado.identificacion }}</p>
      <p>{{ calcularEdad(pacienteSeleccionado.fecha_nacimiento) }} años</p>

      <button class="btn-cambiar" @click="cambiarPaciente">Cambiar paciente</button>
    </div>

    <!-- CASOS -->
    <div v-if="pacienteSeleccionado" class="casos-section">
      <!-- HEADER DESPLEGABLE -->
      <div class="casos-header" @click="mostrarCasos = !mostrarCasos">
        <span class="arrow">
          {{ mostrarCasos ? "▼" : "▶" }}
        </span>
        <label> Casos Disponibles ({{ casosDelPaciente.length }}) </label>
      </div>

      <!-- LISTA DE CASOS -->
      <div v-show="mostrarCasos" class="casos-list">
        <div
          v-for="caso in casosDelPaciente"
          :key="caso.id_caso"
          class="caso-item"
          :class="{ active: casoSeleccionado === caso.id_caso }"
          @click="seleccionarCaso(caso)"
        >
          <div class="caso-header">
            <h4>Caso #{{ caso.id_caso }}</h4>

            <span v-if="estadoCaso" class="caso-badge" :class="'estado-' + estadoCaso">
              {{ getEstadoTexto(estadoCaso) }}
            </span>
          </div>

          <div class="caso-meta">
            <span>📅 {{ formatearFecha(caso.fecha_inicio) }}</span>
            <span>🖼️ {{ resumen.imagenes }} imágenes</span>
          </div>
        </div>
      </div>
    </div>

    <!-- BOTÓN -->
    <button v-if="casoSeleccionado" class="btn-primary" @click="verAnalisis">Segmentar</button>

    <!-- RESUMEN -->
    <div v-if="casoSeleccionado" class="summary-container">
      <div class="summary-header">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="lucide lucide-chart-network"
        >
          <path d="m13.11 7.664 1.78 2.672" />
          <path d="m14.162 12.788-3.324 1.424" />
          <path d="m20 4-6.06 1.515" />
          <path d="M3 3v16a2 2 0 0 0 2 2h16" />
          <circle cx="12" cy="6" r="2" />
          <circle cx="16" cy="12" r="2" />
          <circle cx="9" cy="15" r="2" />
        </svg>
        <h3>Resumen del Caso</h3>
      </div>

      <div class="summary-content">
        <div class="summary-grid">
          <div class="metric-card blue-accent">
            <div class="metric-icon-box">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                class="lucide lucide-camera-icon lucide-camera"
              >
                <path
                  d="M13.997 4a2 2 0 0 1 1.76 1.05l.486.9A2 2 0 0 0 18.003 7H20a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V9a2 2 0 0 1 2-2h1.997a2 2 0 0 0 1.759-1.048l.489-.904A2 2 0 0 1 10.004 4z"
                />
                <circle cx="12" cy="13" r="3" />
              </svg>
            </div>
            <div class="metric-info">
              <b class="metric-value">{{ resumen.imagenes }}</b>
              <span class="metric-label">Imágenes</span>
            </div>
          </div>

          <div class="metric-card purple-accent has-progress">
            <div class="metric-icon-box">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                class="lucide lucide-columns4-icon lucide-columns-4"
              >
                <rect width="18" height="18" x="3" y="3" rx="2" />
                <path d="M7.5 3v18" />
                <path d="M12 3v18" />
                <path d="M16.5 3v18" />
              </svg>
            </div>
            <div class="metric-info">
              <b class="metric-value">{{ resumen.membranas }}</b>
              <span class="metric-label">Membranas</span>
            </div>
            <div class="progress-track">
              <div
                class="progress-fill"
                :style="{ width: calcularPorcentaje(resumen.membranas) + '%' }"
              ></div>
            </div>
          </div>

          <div class="metric-card green-accent has-progress">
            <div class="metric-icon-box">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                class="lucide lucide-eclipse-icon lucide-eclipse"
              >
                <circle cx="12" cy="12" r="10" />
                <path d="M12 2a7 7 0 1 0 10 10" />
              </svg>
            </div>
            <div class="metric-info">
              <b class="metric-value">{{ resumen.nucleos }}</b>
              <span class="metric-label">Núcleos</span>
            </div>
            <div class="progress-track">
              <div
                class="progress-fill"
                :style="{ width: calcularPorcentaje(resumen.nucleos) + '%' }"
              ></div>
            </div>
          </div>

          <div class="metric-card red-accent has-progress">
            <div class="metric-icon-box">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                class="lucide lucide-bubbles-icon lucide-bubbles"
              >
                <path d="M7.001 15.085A1.5 1.5 0 0 1 9 16.5" />
                <circle cx="18.5" cy="8.5" r="3.5" />
                <circle cx="7.5" cy="16.5" r="5.5" />
                <circle cx="7.5" cy="4.5" r="2.5" />
              </svg>
            </div>
            <div class="metric-info">
              <b class="metric-value">{{ resumen.micronucleos }}</b>
              <span class="metric-label">Micronúcleos</span>
            </div>
            <div class="progress-track">
              <div
                class="progress-fill"
                :style="{ width: calcularPorcentaje(resumen.micronucleos) + '%' }"
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </aside>
</template>

<script>
import axios from "axios";

export default {
  name: "SideBar",
  props: { isOpen: Boolean },

  data() {
    return {
      API_URL: "http://127.0.0.1:8000/api",

      pacientes: [],
      pacientesFiltrados: [],
      casosDelPaciente: [],
      analisisDelCaso: [],

      pacienteSeleccionado: null,
      casoSeleccionado: null,

      mostrarDropdown: false,
      mostrarCasos: false,

      busquedaPaciente: "",
      estadoCaso: null,

      resumen: {
        imagenes: 0,
        membranas: 0,
        nucleos: 0,
        micronucleos: 0,
      },
    };
  },

  methods: {
    async cargarPacientes() {
      try {
        console.log("🔍 Cargando pacientes desde:", `${this.API_URL}/pacientes/`);
        const res = await axios.get(`${this.API_URL}/pacientes/`);
        this.pacientes = res.data;
        console.log("✅ Pacientes cargados:", this.pacientes.length);
      } catch (error) {
        console.error("❌ Error cargando pacientes:", error);
        console.error("❌ URL que falló:", error.config?.url);
      }
    },

    filtrarPacientes() {
      const q = this.busquedaPaciente.toLowerCase();

      if (!q) {
        this.pacientesFiltrados = [];
        return;
      }

      this.pacientesFiltrados = this.pacientes.filter(
        (p) =>
          p.nombre.toLowerCase().includes(q) ||
          p.apellido.toLowerCase().includes(q) ||
          p.identificacion.toLowerCase().includes(q),
      );
    },

    async seleccionarPaciente(paciente) {
      this.pacienteSeleccionado = paciente;
      this.busquedaPaciente = `${paciente.nombre} ${paciente.apellido}`;
      this.casoSeleccionado = null;
      this.mostrarDropdown = false;

      this.resetResumen();
      this.$emit("select-patient", paciente.id_paciente);

      try {
        console.log(
          "🔍 Cargando casos desde:",
          `${this.API_URL}/pacientes/${paciente.id_paciente}/casos/`,
        );
        const res = await axios.get(`${this.API_URL}/pacientes/${paciente.id_paciente}/casos/`);
        this.casosDelPaciente = res.data;
        console.log("✅ Casos cargados:", this.casosDelPaciente.length);
      } catch (error) {
        console.error("❌ Error cargando casos:", error);
        console.error("❌ URL que falló:", error.config?.url);
      }
    },

    cambiarPaciente() {
      this.pacienteSeleccionado = null;
      this.casosDelPaciente = [];
      this.analisisDelCaso = [];
      this.casoSeleccionado = null;
      this.busquedaPaciente = "";
      this.mostrarDropdown = false;
      this.resetResumen();
      this.$emit("reset-selection");
    },

    async seleccionarCaso(caso) {
      this.casoSeleccionado = caso.id_caso;
      this.$emit("select-case", caso.id_caso);

      try {
        console.log(
          "🔍 Cargando análisis desde:",
          `${this.API_URL}/casos/${caso.id_caso}/analisis/`,
        );
        const res = await axios.get(`${this.API_URL}/casos/${caso.id_caso}/analisis/`);

        this.analisisDelCaso = res.data;
        this.calcularResumen();
        this.estadoCaso = res.data.length ? res.data[0].estado : null;
        console.log("✅ Análisis cargados:", this.analisisDelCaso.length);
      } catch (error) {
        console.error("❌ Error cargando análisis:", error);
        console.error("❌ URL que falló:", error.config?.url);
      }
    },

    verAnalisis() {
      console.log("Visualizando análisis:", this.casoSeleccionado);
    },

    calcularResumen() {
      const r = {
        imagenes: this.analisisDelCaso.length,
        nucleos: 0,
        membranas: 0,
        micronucleos: 0,
      };

      this.analisisDelCaso.forEach((a) => {
        if (a.resultados?.resultado_jsonb) {
          const m = a.resultados.resultado_jsonb;
          r.nucleos += m.nucleos || 0;
          r.membranas += m.membranas || 0;
          r.micronucleos += m.micronucleos || 0;
        }
      });

      this.resumen = r;
    },

    resetResumen() {
      this.resumen = {
        imagenes: 0,
        nucleos: 0,
        membranas: 0,
        micronucleos: 0,
      };
      this.estadoCaso = null;
    },

    calcularEdad(fecha) {
      const n = new Date(fecha);
      const h = new Date();
      let e = h.getFullYear() - n.getFullYear();
      if (
        h.getMonth() < n.getMonth() ||
        (h.getMonth() === n.getMonth() && h.getDate() < n.getDate())
      )
        e--;
      return e;
    },

    formatearFecha(fecha) {
      return new Date(fecha).toLocaleDateString("es-ES", {
        year: "numeric",
        month: "short",
        day: "numeric",
      });
    },

    getEstadoTexto(estado) {
      const map = {
        pendiente: "Pendiente",
        proceso: "En Proceso",
        listo: "Listo",
        error: "Error",
      };
      return map[estado] || estado;
    },

    calcularPorcentaje(valor) {
      const max = Math.max(this.resumen.nucleos, this.resumen.membranas, this.resumen.micronucleos);
      return max > 0 ? (valor / max) * 100 : 0;
    },
  },

  mounted() {
    this.cargarPacientes();
  },
};
</script>

<style scoped>
.sidebar {
  width: 260px;
  background: #ffffff;
  padding: 15px;
  border-right: 1px solid #e0e0e0;
  overflow-y: auto;
  height: 100%;
}

.sidebar h2 {
  font-size: 18px;
  margin-bottom: 20px;
  color: #2c3e50;
}

/* BÚSQUEDA */
.search-section {
  position: relative;
  margin-bottom: 20px;
}

.search-section label {
  display: block;
  font-size: 12px;
  color: #666;
  margin-bottom: 8px;
  font-weight: 500;
}

.search-input-wrapper {
  position: relative;
}

.search-input-wrapper input {
  width: 100%;
  padding: 10px 40px 10px 12px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.2s ease;
}

.search-input-wrapper input:focus {
  outline: none;
  border-color: #1e88e5;
}

.search-icon {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  opacity: 0.5;
}

/* DROPDOWN PACIENTES */
.pacientes-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  max-height: 300px;
  overflow-y: auto;
  z-index: 100;
  margin-top: 4px;
}

.paciente-item {
  padding: 12px;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
  transition: background 0.2s ease;
}

.paciente-item:hover {
  background: #f8f9fa;
}

.paciente-item:last-child {
  border-bottom: none;
}

.paciente-info strong {
  display: block;
  color: #2c3e50;
  font-size: 14px;
}

.paciente-id {
  display: block;
  color: #999;
  font-size: 12px;
  margin-top: 2px;
}

.no-results {
  padding: 12px;
  text-align: center;
  color: #999;
  font-size: 13px;
  background: #f8f9fa;
  border-radius: 8px;
  margin-top: 8px;
}

/* PACIENTE SELECCIONADO */
.paciente-card {
  background: linear-gradient(135deg, #667eea, #764ba2);
  padding: 10px;
  border-radius: 10px;
  color: white;
  margin-bottom: 14px;
}

.paciente-card h3 {
  margin: 0 0 4px;
  font-size: 14px;
  font-weight: 600;
}

.paciente-card p {
  margin: 2px 0;
  font-size: 11px;
  opacity: 0.9;
}

.btn-cambiar {
  width: 100%;
  margin-top: 8px;
  padding: 6px;
  font-size: 12px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  cursor: pointer;
}

/* CASOS */
.casos-section {
  margin-bottom: 20px;
}

.casos-section label {
  display: block;
  font-size: 12px;
  color: #666;
  margin-bottom: 10px;
  font-weight: 500;
}

.empty-state {
  text-align: center;
  padding: 20px;
  color: #999;
  font-size: 13px;
}

.casos-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.caso-item {
  padding: 12px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.caso-item:hover {
  border-color: #1e88e5;
  background: #f8f9fa;
}

.caso-item.active {
  border-color: #1e88e5;
  background: #e3f2fd;
}

.caso-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.caso-header h4 {
  margin: 0;
  font-size: 14px;
  color: #2c3e50;
  flex: 1;
}

.caso-badge {
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 10px;
  font-weight: 500;
  white-space: nowrap;
}

.estado-0 {
  background: #e3f2fd;
  color: #1976d2;
}

.estado-1 {
  background: #fff3e0;
  color: #f57c00;
}

.estado-2 {
  background: #e8f5e9;
  color: #388e3c;
}

.caso-meta {
  display: flex;
  gap: 12px;
  font-size: 11px;
  color: #666;
}

/* BOTÓN PRINCIPAL */
.btn-primary {
  width: 100%;
  padding: 14px;
  background: #1e88e5;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
  margin-bottom: 20px;
}

.btn-primary:hover {
  background: #1976d2;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(30, 136, 229, 0.3);
}

/* ===================== */
/* RESUMEN ESTILO */
/* ===================== */

.summary-container {
  margin-top: 15px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
  border: 1px solid #edf2f7;
  font-family: "Segoe UI", sans-serif;
}

/* Header más compacto */
.summary-header {
  background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
  padding: 10px 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: white;
  border-top-left-radius: 8px;
  border-top-right-radius: 8px;
}

.summary-header h3 {
  margin: 0;
  font-size: 13px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.summary-content {
  background: #ffffff;
  padding: 8px;
}

.summary-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

/* TARJETA LIMPIA REDUCIDA */
.metric-card {
  background: #ffffff;
  border-radius: 8px;
  padding: 8px 4px 12px 4px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 1px solid #f1f5f9;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;
}

.metric-card.has-progress {
  padding-bottom: 14px;
}

.metric-card:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.06);
}

/* CAJA DEL ICONO */
.metric-icon-box {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 4px;
  flex-shrink: 0;
  color: white;
}

.metric-card.blue-accent .metric-icon-box {
  background: #3182ce;
}
.metric-card.purple-accent .metric-icon-box {
  background: #805ad5;
}
.metric-card.green-accent .metric-icon-box {
  background: #38a169;
}
.metric-card.red-accent .metric-icon-box {
  background: #e53e3e;
}

.metric-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
}

.metric-value {
  font-size: 17px;
  font-weight: 700;
  color: #1e293b;
  line-height: 1;
}

.metric-label {
  font-size: 10px;
  color: #64748b;
  font-weight: 500;
  white-space: nowrap;
  margin-top: 2px;
}

/* ===================== */
/* BARRA DE PROGRESO */
/* ===================== */

.progress-track {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background-color: #f1f5f9;
}

.progress-fill {
  height: 100%;
  width: 0%;
  transition: width 0.5s ease;
}

/* Colores de la barra según el tipo */
.blue-accent .progress-fill {
  background-color: #3182ce;
}
.purple-accent .progress-fill {
  background-color: #805ad5;
}
.green-accent .progress-fill {
  background-color: #38a169;
}
.red-accent .progress-fill {
  background-color: #e53e3e;
}

/*Casos*/
.casos-header {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  user-select: none;
  margin-bottom: 10px;
}

.casos-header label {
  margin: 0;
  line-height: 1;
}

.arrow {
  font-size: 12px;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #1e88e5;
}

/* ===================== */
/* RESPONSIVE - TABLET */
/* ===================== */
@media (max-width: 1200px) {
  .sidebar {
    position: fixed;
    top: 0;
    left: -360px; /* oculto */
    height: 100vh;
    z-index: 1000;
    transition: left 0.3s ease;
    box-shadow: 4px 0 12px rgba(0, 0, 0, 0.15);
  }

  .sidebar.open {
    left: 0;
  }
}

@media (max-width: 1200px) {
  .sidebar {
    width: 300px;
    padding: 16px;
  }

  .sidebar h2 {
    font-size: 16px;
  }
}

.close-btn {
  display: none;
  position: absolute;
  top: 12px;
  right: 12px;
  background: transparent;
  border: none;
  font-size: 22px;
  cursor: pointer;
  color: #555;
}

.paciente-item {
  padding: 10px 12px;
  cursor: pointer;
}

.paciente-item:hover {
  background-color: #f3f4f6;
}

.paciente-nombre {
  font-weight: 600;
  font-size: 15px;
}

.paciente-meta {
  font-size: 13px;
  color: #6b7280;
  margin-top: 2px;
}

@media (max-width: 1200px) {
  .close-btn {
    display: block;
  }
}
</style>
