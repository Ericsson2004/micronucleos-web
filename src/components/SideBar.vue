<template>
  <aside class="sidebar">
    <h2>Selector de Datos Clínicos</h2>

    <div class="form-group">
      <label>ID de Paciente</label>
      <input type="text" v-model="pacienteId" @keyup.enter="buscarPaciente" @blur="buscarPaciente" />
      <div v-if="buscado && pacienteId && !pacienteExiste" class="error-msg">
        ❌ El paciente no existe
      </div>
    </div>

    <div class="form-group">
      <label>Carpeta/Caso de Análisis</label>
        <select v-model="casoSeleccionado" :disabled="!pacienteExiste">
            <option disabled value="">Seleccione la Carpeta</option>
            <option
                v-for="caso in casosPorPaciente[pacienteId] || []"
                :key="caso.id"
                :value="caso.id"
            >
                {{ caso.nombre }}
            </option>
        </select>
        <div v-if="errorCaso" class="error-msg">
            ❌ Seleccione un caso de análisis
        </div>
    </div>

    <button
        class="btn-primary"
        :class="{ activo: analisisEjecutado }"
        @click="ejecutarProcesamiento"
        :disabled="procesando || !pacienteExiste"
    >
        <span v-if="!procesando">Ejecutar Análisis</span>
        <span v-else>Procesando...</span>
    </button>

    <div v-if="procesando" class="progress-container">
        <div class="progress-bar" :style="{ width: progreso + '%' }"></div>
        <span class="progress-text">{{ progreso }}%</span>
    </div>

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
export default {
  name: "SideBar",
  data() {
   return {
    pacienteId: "",
    casoSeleccionado: "",
    analisisEjecutado: false,
    procesando: false,
    progreso: 0,
    buscado: false,
    errorCaso: false,
    casosPorPaciente: {
      "P-1024": [
        { id: "Caso-2023-A", nombre: "Caso 2023-Oct-A", imagenes: 19 },
        { id: "Caso-2024-B", nombre: "Caso 2024-Feb-B", imagenes: 2 },
      ],
      "P-2001": [
        { id: "Caso-2022-X", nombre: "Caso 2022-Jun-X", imagenes: 2 },
      ],
    },
    resumen: {
      imagenes: 0,
      membranas: 0,
      nucleos: 0,
      micronucleos: 0,
    },
   };
  },
computed: {
  pacienteExiste() {
    return !!this.casosPorPaciente[this.pacienteId];
  }
},
 methods: {
    buscarPaciente() {
    this.buscado = true;
    this.casoSeleccionado = "";
    this.analisisEjecutado = false;

    if (this.pacienteExiste) {
    // AVISAMOS AL PADRE (App.vue)
    this.$emit("select-patient", this.pacienteId);
  }
    },

    ejecutarProcesamiento() {
        if (!this.casoSeleccionado) {
        this.errorCaso = true;
        return;
      }

        //EMITIR EJECUCIÓN
        this.$emit("run-analysis", {
        pacienteId: this.pacienteId,
        casoId: this.casoSeleccionado,
    });

      this.procesando = true;
      this.analisisEjecutado = true;
      this.progreso = 0;

      const intervalo = setInterval(() => {
        if (this.progreso < 100) {
          this.progreso += 5;
        } else {
          clearInterval(intervalo);

          // RESULTADOS DEL ANÁLISIS
          this.resumen.membranas = 145;
          this.resumen.nucleos = 12;
          this.resumen.micronucleos = 5;

          this.procesando = false;
        }
      }, 150);
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

      // Resetear resumen
      this.resumen = {
        imagenes: 0,
        membranas: 0,
        nucleos: 0,
        micronucleos: 0,
      };

      if (nuevoCaso) {
        const caso = this.casosPorPaciente[this.pacienteId]
          .find(c => c.id === nuevoCaso);

        if (caso) {
          this.resumen.imagenes = caso.imagenes;
        }

        this.$emit("select-case", nuevoCaso);
      }
    },
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
