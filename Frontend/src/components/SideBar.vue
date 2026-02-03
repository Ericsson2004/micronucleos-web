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

      <div
        v-if="mostrarDropdown && pacientesFiltrados.length > 0"
        class="pacientes-dropdown"
      >
        <div
          v-for="paciente in pacientesFiltrados.slice(0, 5)"
          :key="paciente.id_paciente"
          class="paciente-item"
          @click="seleccionarPaciente(paciente)"
        >
          <div class="paciente-nombre">
            {{ paciente.nombre }} {{ paciente.apellido }}
          </div>

          <div class="paciente-meta">
            ID: {{ paciente.identificacion }}
          </div>
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

      <button class="btn-cambiar" @click="cambiarPaciente">
        Cambiar paciente
      </button>
    </div>

    <!-- CASOS -->
    <div v-if="pacienteSeleccionado" class="casos-section">
      <label>Casos Disponibles ({{ casosDelPaciente.length }})</label>

      <div
        v-for="caso in casosDelPaciente"
        :key="caso.id_caso"
        class="caso-item"
        :class="{ active: casoSeleccionado === caso.id_caso }"
        @click="seleccionarCaso(caso)"
      >
        <div class="caso-header">
          <!-- 🔧 antes: caso.titulo -->
          <h4>Caso #{{ caso.id_caso }}</h4>

          <!-- 🔧 estado ahora viene del análisis -->
          <span
            v-if="estadoCaso"
            class="caso-badge"
            :class="'estado-' + estadoCaso"
          >
            {{ getEstadoTexto(estadoCaso) }}
          </span>
        </div>

        <div class="caso-meta">
          <!-- 🔧 antes: fecha_creacion -->
          <span>📅 {{ formatearFecha(caso.fecha_inicio) }}</span>
          <span>🖼️ {{ resumen.imagenes }} imágenes</span>
        </div>
      </div>
    </div>

    <!-- BOTÓN -->
    <button v-if="casoSeleccionado" class="btn-primary" @click="verAnalisis">
      📊 Ver Análisis Completo
    </button>

    <!-- RESUMEN -->
    <div v-if="casoSeleccionado" class="summary-panel">
      <h3>Resumen del Caso</h3>
      <div class="summary-grid">
        <div class="summary-card images">
          <b>{{ resumen.imagenes }}</b>
          <span>Imágenes</span>
        </div>
      
        <div class="summary-card membranes">
          <b>{{ resumen.membranas }}</b>
          <span>Membranas</span>
        </div>
      
        <div class="summary-card nuclei">
          <b>{{ resumen.nucleos }}</b>
          <span>Núcleos</span>
        </div>
      
        <div class="summary-card micro">
          <b>{{ resumen.micronucleos }}</b>
          <span>Micronúcleos</span>
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
      API_URL: "http://127.0.0.1:8000",

      pacientes: [],
      pacientesFiltrados: [],
      casosDelPaciente: [],
      analisisDelCaso: [],

      pacienteSeleccionado: null,
      casoSeleccionado: null,

      mostrarDropdown: false,

      busquedaPaciente: "",
      estadoCaso: null,

      resumen: {
        imagenes: 0,
        membranas: 0,
        nucleos: 0,
        micronucleos: 0
      }
    };
  },

  methods: {
    async cargarPacientes() {
      const res = await axios.get(`${this.API_URL}/api/pacientes/`);
      this.pacientes = res.data;
    },

    filtrarPacientes() {
      const q = this.busquedaPaciente.toLowerCase();

      if (!q) {
        this.pacientesFiltrados = [];
        return;
      }
    
      this.pacientesFiltrados = this.pacientes.filter(p =>
        p.nombre.toLowerCase().includes(q) ||
        p.apellido.toLowerCase().includes(q) ||
        p.identificacion.toLowerCase().includes(q)
      );
    },

    async seleccionarPaciente(paciente) {
      this.pacienteSeleccionado = paciente;
      this.busquedaPaciente = `${paciente.nombre} ${paciente.apellido}`;
      this.casoSeleccionado = null;
      this.mostrarDropdown = false;

      this.resetResumen();

      this.$emit('select-patient', paciente.id_paciente);  
    
      try {
        const res = await axios.get(
          `${this.API_URL}/api/pacientes/${paciente.id_paciente}/casos/`
        );
        this.casosDelPaciente = res.data;
      } catch (e) {
        console.error("Error cargando casos", e);
      }
    },

    cambiarPaciente() {
      this.pacienteSeleccionado = null;
      this.casosDelPaciente = [];
      this.analisisDelCaso = [];
      this.resetResumen();
    },

    async seleccionarCaso(caso) {
      this.casoSeleccionado = caso.id_caso;
      
      this.$emit('select-case', caso.id_caso);

      try {
        const res = await axios.get(
          `${this.API_URL}/api/casos/${caso.id_caso}/analisis/`
        );

        this.analisisDelCaso = res.data;
        this.calcularResumen();

        this.estadoCaso = res.data.length
          ? res.data[0].estado
          : null;
      } catch (e) {
        console.error("Error cargando detalle del caso", e);
      }
    },

    verAnalisis() {
      console.log("Visualizando análisis completo del caso:", this.casoSeleccionado);
      
    },

    calcularResumen() {
      const r = {
        imagenes: this.analisisDelCaso.length,
        nucleos: 0,
        membranas: 0,
        micronucleos: 0
      };

      this.analisisDelCaso.forEach(a => {
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
        micronucleos: 0
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
      ) e--;
      return e;
    },

    getEstadoTexto(e) {
      return {
        pendiente: "Pendiente",
        proceso: "En proceso",
        listo: "Listo",
        error: "Error"
      }[e];
    },

    formatearFecha(f) {
      return new Date(f).toLocaleDateString();
    }
  },

  mounted() {
    this.cargarPacientes();
  }
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
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 16px;
  border-radius: 12px;
  color: white;
  margin-bottom: 20px;
}

.paciente-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.paciente-avatar {
  width: 50px;
  height: 50px;
  background: rgba(255,255,255,0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: bold;
  color: white;
}

.paciente-datos h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.paciente-datos p {
  margin: 2px 0;
  font-size: 12px;
  opacity: 0.9;
}

.edad {
  font-size: 11px;
  opacity: 0.8;
}

.btn-cambiar {
  width: 100%;
  padding: 8px;
  background: rgba(255,255,255,0.2);
  border: 1px solid rgba(255,255,255,0.3);
  color: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s ease;
}

.btn-cambiar:hover {
  background: rgba(255,255,255,0.3);
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

/* RESUMEN */
.summary-panel {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 12px;
  border: 1px solid #e0e0e0;
}

.summary-panel h3 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #2c3e50;
  text-align: center;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.summary-card {
  padding: 14px 10px;
  border-radius: 10px;
  text-align: center;
  color: white;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.summary-card b {
  display: block;
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 4px;
}

.summary-card span {
  font-size: 11px;
  opacity: 0.9;
}

.summary-card.images {
  background: linear-gradient(135deg, #42a5f5, #1e88e5);
}

.summary-card.membranes {
  background: linear-gradient(135deg, #8d6e63, #6d4c41);
}

.summary-card.nuclei {
  background: linear-gradient(135deg, #66bb6a, #43a047);
}

.summary-card.micro {
  background: linear-gradient(135deg, #ef5350, #e53935);
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
    box-shadow: 4px 0 12px rgba(0,0,0,0.15);
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


