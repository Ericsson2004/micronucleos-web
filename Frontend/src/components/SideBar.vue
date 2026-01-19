<template>
  <aside class="sidebar">
    <h2>Selector de Datos Clínicos</h2>

    <!-- PACIENTE -->
    <div class="form-group">
      <label>ID de Paciente</label>
      <input
        type="text"
        v-model="pacienteId"
        placeholder="Ej: 1024"
        @keyup.enter="buscarPaciente"
        @blur="buscarPaciente"
      />

      <div v-if="buscado && pacienteId && !pacienteExiste" class="error-msg">
        El paciente no existe
      </div>
    </div>

    <!-- CASO -->
    <div class="form-group">
      <label>Carpeta / Caso de Análisis</label>
      <select
        v-model="casoSeleccionado"
        :disabled="!pacienteExiste"
      >
        <option disabled value="">Seleccione el Caso</option>

        <option
          v-for="caso in casosPorPaciente[pacienteId] || []"
          :key="caso.id"
          :value="caso.id"
        >
          {{ caso.nombre }}
        </option>
      </select>

      <div v-if="errorCaso" class="error-msg">
        Seleccione un caso de análisis
      </div>
    </div>

    <!-- BOTÓN -->
    <button
      class="btn-primary"
      :class="{ activo: analisisEjecutado }"
      :disabled="procesando || !pacienteExiste"
      @click="ejecutarProcesamiento"
    >
      <span v-if="!procesando">Ver Caso</span>
      <span v-else>Procesando...</span>
    </button>

    <!-- PROGRESO -->
    <div v-if="procesando" class="progress-container">
      <div class="progress-bar" :style="{ width: progreso + '%' }"></div>
      <span class="progress-text">{{ progreso }}%</span>
    </div>

    <!-- RESUMEN -->
    <div class="summary-panel">
      <h3>Resumen Global</h3>

      <div class="summary-grid">
        <div class="summary-card images">
          <b>{{ resumen.imagenes }}</b>
          <span>Total Imágenes</span>
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

  data() {
    return {
      API_URL: "http://127.0.0.1:8000",

      // API
      analisis: [],
      loading: true,

      // UI state
      pacienteId: "",
      casoSeleccionado: "",
      buscado: false,
      errorCaso: false,
      analisisEjecutado: false,
      procesando: false,
      progreso: 0,

      // Resumen (se recalcula)
      resumen: {
        imagenes: 0,
        membranas: 0,
        nucleos: 0,
        micronucleos: 0,
      },
    };
  },

  computed: {
    // Agrupa análisis por paciente
    casosPorPaciente() {
      const map = {};

      this.analisis.forEach(a => {
        const paciente = String(a.id_paciente_fk);

        if (!map[paciente]) {
          map[paciente] = [];
        }

        map[paciente].push({
          id: String(a.id_caso_fk),
          nombre: `Caso ${a.id_caso_fk}`,
          analisis: a,
        });
      });

      return map;
    },

    // Verifica si el paciente existe
    pacienteExiste() {
      return !!this.casosPorPaciente[this.pacienteId];
    },
  },

  methods: {
    buscarPaciente() {
      this.buscado = true;
      this.casoSeleccionado = "";
      this.analisisEjecutado = false;
      this.errorCaso = false;

      if (this.pacienteExiste) {
        // Avisamos al padre
        this.$emit("select-patient", this.pacienteId);
      }
    },

    ejecutarProcesamiento() {
      if (!this.casoSeleccionado) {
        this.errorCaso = true;
        return;
      }

      // Emitimos selección completa
      this.$emit("run-analysis", {
        pacienteId: this.pacienteId,
        casoId: this.casoSeleccionado,
      });

      this.$emit("select-case", this.casoSeleccionado);

      // Simulación visual de procesamiento
      this.procesando = true;
      this.analisisEjecutado = true;
      this.progreso = 0;

      const intervalo = setInterval(() => {
        if (this.progreso < 100) {
          this.progreso += 5;
        } else {
          clearInterval(intervalo);
          this.procesando = false;
        }
      }, 150);
    },

    calcularResumen(analisis) {
      const resumen = {
        imagenes: 0,
        membranas: 0,
        nucleos: 0,
        micronucleos: 0,
      };

      if (!analisis) return resumen;

      analisis.muestras_saliva.forEach(muestra => {
        resumen.imagenes += 1;

        muestra.resultados.forEach(r => {
          resumen.nucleos += r.nucleos || 0;
          resumen.membranas += r.membranas || 0;
          resumen.micronucleos += r.micronucleos || 0;
        });
      });

      return resumen;
    },
  },

  watch: {
    pacienteId() {
      this.buscado = false;
      this.casoSeleccionado = "";
      this.analisisEjecutado = false;
      this.errorCaso = false;
      this.resumen = {
        imagenes: 0,
        membranas: 0,
        nucleos: 0,
        micronucleos: 0,
      };
    },

    casoSeleccionado(nuevoCaso) {
      this.errorCaso = false;

      if (!nuevoCaso) return;

      const analisis = this.casosPorPaciente[this.pacienteId]
        ?.find(a => a.id === nuevoCaso)?.analisis;

      this.resumen = this.calcularResumen(analisis);
    },
  },

  mounted() {
    axios
      .get(`${this.API_URL}/api/analisis/`)
      .then(res => {
        this.analisis = res.data;
      })
      .catch(err => {
        console.error("SideBar API error:", err);
      })
      .finally(() => {
        this.loading = false;
      });
  },
};
</script>

<style scoped>
.sidebar {
  width: 320px;
  background: #f8f9fb;
  padding: 16px;
  border-right: 1px solid #ddd;
}

.form-group {
  margin-bottom: 12px;
}

.form-group label {
  display: block;
  font-size: 13px;
  color: #555;
  margin-bottom: 4px;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 6px 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.btn-primary {
  width: 100%;
  padding: 10px;
  margin-top: 12px;
  background: #e0e0e0;
  color: #333;
  border: 1px solid #bbb;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

/*cuando se ejecuta el análisis */
.btn-primary.activo {
  background: #1e88e5;
  color: #fff;
  border-color: #1e88e5;
}

button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.summary-panel {
  margin-top: 18px;
  padding: 16px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #ddd;
  text-align: center;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

.summary-grid div {
  text-align: center;
}

.summary-grid b {
  font-size: 20px;
  display: block;
}

.summary-card {
  padding: 16px 10px;
  border-radius: 12px;
  color: #fff;
  box-shadow: 0 4px 10px rgba(0,0,0,0.08);
}

.summary-card span {
  font-size: 12px;
  color: #ffffff;
  opacity: 0.9;
}

.summary-card b {
  font-size: 26px;
  display: block;
  font-weight: 600;
}

.summary-card span {
  font-size: 12px;
  opacity: 0.9;
}

/* Colores */
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

.progress-container {
  margin-top: 12px;
}

.progress-bar {
  height: 8px;
  background: #1e88e5;
  border-radius: 4px;
  transition: width 0.15s ease;
}

.progress-text {
  font-size: 12px;
  text-align: right;
  margin-top: 4px;
  color: #555;
}

.error-msg {
  margin-top: 6px;
  font-size: 12px;
  color: #d32f2f;
  background: #fdecea;
  padding: 6px 8px;
  border-radius: 6px;
}
</style>