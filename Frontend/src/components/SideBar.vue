<template>
  <aside class="sidebar" :class="{ open: isOpen }">
    <button class="close-btn" @click="$emit('close-sidebar')">✕</button>
    <h2>Búsqueda de Casos</h2>

    <!-- BUSCADOR DE PACIENTE -->
    <div class="search-section" v-click-outside="cerrarDropdown">
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
          @mousedown.prevent="seleccionarPaciente(paciente)"
        >
          <div class="paciente-nombre">{{ paciente.nombre }} {{ paciente.apellido }}</div>
          <div class="paciente-meta">ID: {{ paciente.identificacion }}</div>
        </div>
      </div>
    </div>

    <!-- PACIENTE SELECCIONADO -->
    <div v-if="pacienteSeleccionado" class="paciente-card">
      <h3>{{ pacienteSeleccionado.nombre }} {{ pacienteSeleccionado.apellido }}</h3>
      <p>ID: {{ pacienteSeleccionado.identificacion }}</p>
      <p>{{ calcularEdad(pacienteSeleccionado.fecha_nacimiento) }} años</p>
      <button class="btn-cambiar" @click="cambiarPaciente">Cambiar paciente</button>
    </div>

    <!-- CASOS -->
    <div v-if="pacienteSeleccionado" class="casos-section">
      <div class="casos-header" @click="mostrarCasos = !mostrarCasos">
        <span class="arrow">{{ mostrarCasos ? "▼" : "▶" }}</span>
        <label>Casos Disponibles ({{ casosDelPaciente.length }})</label>
      </div>

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
            <!-- ✅ FIX: caso.estado en lugar de estadoCaso global -->
            <span v-if="caso.estado" class="caso-badge" :class="'estado-' + caso.estado">
              {{ getEstadoTexto(caso.estado) }}
            </span>
          </div>

          <div class="caso-meta">
            <span class="meta-item">
              <svg
                class="meta-icon"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                <line x1="16" y1="2" x2="16" y2="6"></line>
                <line x1="8" y1="2" x2="8" y2="6"></line>
                <line x1="3" y1="10" x2="21" y2="10"></line>
              </svg>
              {{ formatearFecha(caso.fecha_inicio) }}
            </span>
            <span class="meta-item">
              <svg
                class="meta-icon"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                <circle cx="8.5" cy="8.5" r="1.5"></circle>
                <polyline points="21 15 16 10 5 21"></polyline>
              </svg>
              {{ resumen.imagenes }} imágenes
            </span>
          </div>
        </div>

        <div v-if="casosDelPaciente.length === 0" class="casos-empty">Sin casos registrados</div>
      </div>
    </div>

    <!-- SEGMENTAR + ESTADO DEL JOB -->
    <div v-if="casoSeleccionado" class="segmentar-section">
      <!-- Job corriendo: barra de progreso -->
      <div v-if="jobCorriendo" class="job-progress">
        <div class="job-progress-header">
          <span class="job-spinner">⟳</span>
          <span class="job-titulo">Analizando...</span>
          <span class="job-porcentaje">{{ job.progreso_porcentaje }}%</span>
        </div>
        <div class="job-bar-track">
          <div class="job-bar-fill" :style="{ width: job.progreso_porcentaje + '%' }"></div>
        </div>
        <p class="job-detalle">
          <template v-if="job.total_imagenes > 0">
            {{ job.procesadas }} de {{ job.total_imagenes }} imagen{{
              job.total_imagenes !== 1 ? "es" : ""
            }}
          </template>
          <template v-else> Preparando imágenes... </template>
        </p>
      </div>

      <div v-else-if="jobReciente && job && job.estado === 'completado'" class="job-ok">
        Análisis completado —
        {{
          job.total_imagenes > 0
            ? job.total_imagenes + " imagen" + (job.total_imagenes !== 1 ? "es" : "")
            : "todas las imágenes"
        }}
      </div>

      <!-- Error -->
      <div v-else-if="job && job.estado === 'error'" class="job-error">
        Fallo en {{ job.errores }} imagen{{ job.errores !== 1 ? "es" : "" }}
      </div>

      <!-- Confirmacion reproceso -->
      <div v-if="mostrarConfirmacion" class="job-confirmacion">
        <p>Todas las imagenes ya fueron analizadas. Deseas ejecutar un nuevo analisis?</p>
        <div class="confirmacion-btns">
          <button class="btn-confirmar" @click="confirmarAnalisis">Si, re-analizar</button>
          <button class="btn-cancelar" @click="mostrarConfirmacion = false">Cancelar</button>
        </div>
      </div>

      <!-- Boton principal -->
      <button
        v-if="!mostrarConfirmacion"
        class="btn-primary"
        :class="{ 'btn-reproceso': esReproceso }"
        :disabled="jobCorriendo"
        @click="verAnalisis"
      >
        <span v-if="jobCorriendo">Procesando...</span>
        <span v-else-if="esReproceso">Re-analizar caso</span>
        <span v-else>Segmentar</span>
      </button>
    </div>

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
                class="elegant-icon"
                viewBox="0 0 24 24"
                fill="none"
                stroke="#ffffff"
                stroke-width="1.5"
              >
                <path
                  d="M4 12c0-4.418 3.582-8 8-8s8 3.582 8 8-3.582 8-8 8-8-3.582-8-8z"
                  stroke-dasharray="3 3"
                />
                <circle cx="12" cy="12" r="5" stroke="#ffffff" />
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
                class="elegant-icon"
                viewBox="0 0 24 24"
                fill="none"
                stroke="#ffffff"
                stroke-width="1.5"
              >
                <circle cx="12" cy="12" r="8" />
                <circle cx="12" cy="12" r="3" fill="#ffffff" stroke="none" />
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
                class="elegant-icon"
                viewBox="0 0 24 24"
                fill="none"
                stroke="#ffffff"
                stroke-width="1.5"
              >
                <circle cx="12" cy="12" r="5" />
                <circle cx="12" cy="12" r="1.5" fill="#ffffff" stroke="none" />
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

  // ✅ Directiva personalizada para cerrar dropdown al hacer click fuera
  directives: {
    clickOutside: {
      mounted(el, binding) {
        el._clickOutsideHandler = (event) => {
          if (!el.contains(event.target)) {
            binding.value();
          }
        };
        document.addEventListener("mousedown", el._clickOutsideHandler);
      },
      unmounted(el) {
        document.removeEventListener("mousedown", el._clickOutsideHandler);
      },
    },
  },

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

      // Job de analisis
      job: null,
      esReproceso: false,
      jobReciente: false,
      mostrarConfirmacion: false,
      pollingTimer: null,
    };
  },

  computed: {
    jobCorriendo() {
      return this.job && ["pendiente", "en_proceso"].includes(this.job.estado);
    },
  },

  methods: {
    async cargarPacientes() {
      try {
        const res = await axios.get(`${this.API_URL}/pacientes/`);
        this.pacientes = res.data;
        console.log("✅ Pacientes cargados:", this.pacientes.length);
      } catch (error) {
        console.error("❌ Error cargando pacientes:", error);
      }
    },

    filtrarPacientes() {
      const q = this.busquedaPaciente.toLowerCase().trim();

      if (!q) {
        this.pacientesFiltrados = [];
        this.mostrarDropdown = false;
        return;
      }

      this.pacientesFiltrados = this.pacientes.filter(
        (p) =>
          p.nombre.toLowerCase().includes(q) ||
          p.apellido.toLowerCase().includes(q) ||
          p.identificacion.toLowerCase().includes(q),
      );
      this.mostrarDropdown = true;
    },

    cerrarDropdown() {
      this.mostrarDropdown = false;
    },

    // ✅ FIX CLAVE: @mousedown.prevent en los items del dropdown.
    // Sin esto: blur del input se dispara ANTES del click → cierra el dropdown
    // → la selección nunca se registra. mousedown ocurre antes que blur.
    async seleccionarPaciente(paciente) {
      this.pacienteSeleccionado = paciente;
      this.busquedaPaciente = `${paciente.nombre} ${paciente.apellido}`;
      this.casoSeleccionado = null;
      this.mostrarDropdown = false;
      this.pacientesFiltrados = [];
      this.resetResumen();
      this.$emit("select-patient", paciente.id_paciente);

      try {
        const res = await axios.get(`${this.API_URL}/pacientes/${paciente.id_paciente}/casos/`);
        this.casosDelPaciente = res.data;
        this.mostrarCasos = this.casosDelPaciente.length > 0;
        console.log("✅ Casos cargados:", this.casosDelPaciente.length);
      } catch (error) {
        console.error("❌ Error cargando casos:", error);
      }
    },

    cambiarPaciente() {
      this.pacienteSeleccionado = null;
      this.casosDelPaciente = [];
      this.analisisDelCaso = [];
      this.casoSeleccionado = null;
      this.busquedaPaciente = "";
      this.mostrarDropdown = false;
      this.pacientesFiltrados = [];
      this.mostrarCasos = false;
      this.resetResumen();
      this.detenerPolling();
      this.job = null;
      this.esReproceso = false;
      this.jobReciente = false;
      this.mostrarConfirmacion = false;
      this.$emit("reset-selection");
    },

    async seleccionarCaso(caso) {
      this.casoSeleccionado = caso.id_caso;
      this.$emit("select-case", caso.id_caso);

      // Resetear estado del job al cambiar de caso
      this.detenerPolling();
      this.job = null;
      this.esReproceso = false;
      this.jobReciente = false;
      this.mostrarConfirmacion = false;

      try {
        const [analisisRes, jobRes] = await Promise.all([
          axios.get(`${this.API_URL}/casos/${caso.id_caso}/analisis/`),
          axios.get(`${this.API_URL}/casos/${caso.id_caso}/job-activo/`),
        ]);

        this.analisisDelCaso = analisisRes.data;
        this.calcularResumen();

        const jobData = jobRes.data;
        this.esReproceso = jobData.es_reproceso || false;

        if (jobData.hay_job_activo) {
          this.job = jobData.job;
          this.iniciarPolling();
        } else if (jobData.job) {
          this.job = jobData.job;
          if (jobData.job.estado === "completado") {
            this.jobReciente = true;
            // Notificar a MainContent para que cargue las imágenes ya segmentadas
            this.$emit("analisis-completado", this.casoSeleccionado);
            setTimeout(() => {
              this.jobReciente = false;
            }, 5000);
          }
        }

        console.log("Analisis cargados:", this.analisisDelCaso.length);
      } catch (error) {
        console.error("Error cargando caso:", error);
      }
    },

    async verAnalisis() {
      if (this.jobCorriendo) return;

      // Si es reproceso mostrar confirmacion
      if (this.esReproceso) {
        this.mostrarConfirmacion = true;
        return;
      }

      await this.lanzarAnalisis();
    },

    async confirmarAnalisis() {
      this.mostrarConfirmacion = false;
      await this.lanzarAnalisis();
    },

    async lanzarAnalisis() {
      try {
        const res = await axios.post(
          `${this.API_URL}/casos/${this.casoSeleccionado}/analizar/`,
          {},
        );

        this.job = {
          id_job: res.data.job_id, // el POST devuelve job_id, lo normalizamos a id_job
          estado: "pendiente",
          progreso_porcentaje: 0,
          procesadas: 0,
          total_imagenes: 0,
        };
        this.esReproceso = res.data.es_reproceso || false;
        this.jobReciente = false;
        this.iniciarPolling();
      } catch (error) {
        if (error.response?.status === 409) {
          // Ya hay un job activo - recuperarlo
          const jobId = error.response.data.job_id;
          if (jobId) {
            const jobRes = await axios.get(`${this.API_URL}/jobs/${jobId}/`);
            this.job = jobRes.data; // el serializer ya devuelve id_job correcto
            this.iniciarPolling();
          }
        } else {
          console.error("Error lanzando analisis:", error);
        }
      }
    },

    iniciarPolling() {
      this.detenerPolling();
      this.pollingTimer = setInterval(async () => {
        if (!this.job?.id_job) {
          this.detenerPolling();
          return;
        }

        try {
          const res = await axios.get(`${this.API_URL}/jobs/${this.job.id_job}/`);
          this.job = res.data;

          // ── Recargar resumen y galería en CADA tick mientras procesa ──
          if (["en_proceso", "completado"].includes(res.data.estado)) {
            const analisisRes = await axios.get(
              `${this.API_URL}/casos/${this.casoSeleccionado}/analisis/`,
            );
            this.analisisDelCaso = analisisRes.data;
            this.calcularResumen();
            // Notificar a MainContent para que actualice la galería en tiempo real
            this.$emit("analisis-progreso", this.casoSeleccionado);
          }

          if (["completado", "error"].includes(res.data.estado)) {
            this.detenerPolling();

            if (res.data.estado === "completado") {
              this.jobReciente = true;
              this.$emit("analisis-completado", this.casoSeleccionado);
              setTimeout(() => {
                this.jobReciente = false;
              }, 6000);
            }

            // Actualizar si ahora es reproceso
            const jobRes = await axios.get(
              `${this.API_URL}/casos/${this.casoSeleccionado}/job-activo/`,
            );
            this.esReproceso = jobRes.data.es_reproceso || false;
          }
        } catch (error) {
          console.error("Error en polling:", error);
        }
      }, 4000);
    },

    detenerPolling() {
      if (this.pollingTimer) {
        clearInterval(this.pollingTimer);
        this.pollingTimer = null;
      }
    },

    calcularResumen() {
      const r = {
        imagenes: this.analisisDelCaso.length,
        nucleos: 0,
        membranas: 0,
        micronucleos: 0,
      };

      this.analisisDelCaso.forEach((a) => {
        // ✅ FIX: leer de AnalisisResultados (campos tipados) en lugar de resultado_jsonb
        if (a.resultados) {
          r.nucleos += a.resultados.total_nucleos || 0;
          r.membranas += a.resultados.total_membranas || 0;
          r.micronucleos += a.resultados.total_micronucleos || 0;
          return;
        }

        // Fallback: contar objetos desde el archivo JSON activo
        const archivoActivo = a.archivos?.find((arch) => arch.activo);
        if (archivoActivo?.contenido_json?.objetos) {
          const objetos = archivoActivo.contenido_json.objetos;
          r.nucleos += objetos.filter((o) => o.tipo === "nucleo").length;
          r.membranas += objetos.filter((o) => o.tipo === "membrana").length;
          r.micronucleos += objetos.filter((o) => o.tipo === "micronucleo").length;
        }
      });

      this.resumen = r;
    },

    resetResumen() {
      this.resumen = { imagenes: 0, nucleos: 0, membranas: 0, micronucleos: 0 };
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
      return (
        { pendiente: "Pendiente", proceso: "En Proceso", listo: "Listo", error: "Error" }[estado] ||
        estado
      );
    },

    calcularPorcentaje(valor) {
      const max = Math.max(
        this.resumen.nucleos,
        this.resumen.membranas,
        this.resumen.micronucleos,
        1,
      );
      return (valor / max) * 100;
    },
  },

  mounted() {
    this.cargarPacientes();
  },

  unmounted() {
    this.detenerPolling();
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

.meta-icon {
  width: 13px; /* Hazlos de 12px o 13px */
  height: 13px;
  stroke: #667eea;
  opacity: 0.8;
  stroke-width: 1.5; /* Línea más delgada para que se vea elegante en chiquito */
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

/* ===================== */
/* SEGMENTAR + JOB       */
/* ===================== */

.segmentar-section {
  margin-bottom: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* Barra de progreso del job */
.job-progress {
  background: #f0f4ff;
  border: 1px solid #c7d7f9;
  border-radius: 10px;
  padding: 12px 14px;
}

.job-progress-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
}

.job-spinner {
  font-size: 16px;
  animation: spin 1.2s linear infinite;
  display: inline-block;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.job-titulo {
  flex: 1;
  font-size: 12px;
  font-weight: 600;
  color: #3730a3;
}

.job-porcentaje {
  font-size: 13px;
  font-weight: 700;
  color: #4f46e5;
}

.job-bar-track {
  width: 100%;
  height: 6px;
  background: #dde3f8;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 6px;
}

.job-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 4px;
  transition: width 0.5s ease;
}

.job-detalle {
  font-size: 11px;
  color: #6366f1;
  margin: 0;
  text-align: right;
}

/* Completado */
.job-ok {
  background: #f0fdf4;
  border: 1px solid #86efac;
  border-radius: 8px;
  padding: 10px 12px;
  font-size: 12px;
  font-weight: 500;
  color: #166534;
}

/* Error */
.job-error {
  background: #fff1f2;
  border: 1px solid #fca5a5;
  border-radius: 8px;
  padding: 10px 12px;
  font-size: 12px;
  font-weight: 500;
  color: #991b1b;
}

/* Confirmacion reproceso */
.job-confirmacion {
  background: #fffbeb;
  border: 1px solid #fcd34d;
  border-radius: 10px;
  padding: 12px;
}

.job-confirmacion p {
  font-size: 12px;
  color: #92400e;
  margin: 0 0 10px 0;
  line-height: 1.5;
}

.confirmacion-btns {
  display: flex;
  gap: 8px;
}

.btn-confirmar {
  flex: 1;
  padding: 7px;
  background: #f59e0b;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
  font-family: inherit;
}
.btn-confirmar:hover {
  background: #d97706;
}

.btn-cancelar {
  flex: 1;
  padding: 7px;
  background: white;
  color: #6b7280;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
}
.btn-cancelar:hover {
  background: #f3f4f6;
}

/* Boton re-analizar */
.btn-primary.btn-reproceso {
  background: linear-gradient(135deg, #667eea, #764ba2);
}
.btn-primary.btn-reproceso:hover {
  background: linear-gradient(135deg, #5a6fd6, #6a3f91);
  box-shadow: 0 4px 12px rgba(118, 75, 162, 0.3);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}
</style>
