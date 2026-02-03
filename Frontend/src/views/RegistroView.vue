<template>
  <div class="content">
    <div class="center-container">

    <header class="page-header">
      <div>
        <h2>Registro Clínico</h2>
      </div>
    </header>

    <div class="tabs-container">
      <button class="tab-btn" :class="{ active: vistaActiva === 'paciente' }" @click="vistaActiva = 'paciente'">
        Paciente
      </button>
      <button class="tab-btn" :class="{ active: vistaActiva === 'caso' }" @click="vistaActiva = 'caso'">
        Caso Clínico
      </button>
      <button class="tab-btn" :class="{ active: vistaActiva === 'muestra' }" @click="vistaActiva = 'muestra'">
        Muestra
      </button>
    </div>

    <!-- ================= PACIENTE ================= -->
    <div v-if="vistaActiva === 'paciente'" class="form-wrapper">
      <div class="card">
        <div class="card-header">
          <h3>Paciente</h3>
        </div>

        <div class="card-body">
          <form @submit.prevent="crearPaciente">
            <div class="form-grid">
              <input v-model="paciente.nombre" placeholder="Nombre" required />
              <input v-model="paciente.apellido" placeholder="Apellido" required />
              <input v-model="paciente.identificacion" placeholder="Identificación" required />
              <input v-model="paciente.fecha_nacimiento" type="date" required />
              <input v-model="paciente.email" placeholder="Email" />
              <input v-model="paciente.telefono" placeholder="Teléfono" />
            </div>

            <div class="form-actions">
              <button class="btn-primary">Guardar Paciente</button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- ================= CASO ================= -->
    <div v-if="vistaActiva === 'caso'" class="form-wrapper">
      <div class="card">
        <div class="card-header">
          <h3>Caso Clínico</h3>
        </div>

        <div class="card-body">
          <form @submit.prevent="crearCaso">
            <div class="form-group">
              <label>Paciente</label>
              <select v-model="caso.id_paciente_fk" required>
                <option value="">Seleccione</option>
                <option v-for="p in pacientes" :key="p.id_paciente" :value="p.id_paciente">
                  {{ p.nombre }} {{ p.apellido }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label>Diagnóstico</label>
              <textarea v-model="caso.diagnostico" rows="4"></textarea>
            </div>

            <div class="form-group">
              <label>Estado</label>
              <select v-model="caso.estado">
                <option value="abierto">Abierto</option>
                <option value="en_proceso">En Proceso</option>
                <option value="cerrado">Cerrado</option>
              </select>
            </div>

            <div class="form-actions">
              <button class="btn-primary">Guardar Caso</button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- ================= MUESTRA ================= -->
    <div v-if="vistaActiva === 'muestra'" class="form-wrapper">
      <div class="card">
        <div class="card-header">
          <h3>Muestra</h3>
        </div>

        <div class="card-body">
          <form @submit.prevent="crearMuestra">
            <div class="form-group">
              <label>Caso Clínico</label>
              <select v-model="muestra.id_caso_fk" required>
                <option value="">Seleccione</option>
                <option v-for="c in casos" :key="c.id_caso" :value="c.id_caso">
                  Caso #{{ c.id_caso }} - {{ getPacienteNombre(c.id_paciente_fk) }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label>Tipo de Muestra</label>
              <select v-model="muestra.tipo_muestra">
                <option value="saliva">Saliva</option>
                <option value="sangre">Sangre</option>
              </select>
            </div>

            <div class="form-group">
              <label>Imagen</label>
              <input type="file" accept="image/*"  @change="onFile" required />
            </div>

            <div class="form-actions">
              <button class="btn-primary" :disabled="!muestra.ruta_imagen">Guardar Muestra</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      API: 'http://127.0.0.1:8000/api',
      vistaActiva: 'paciente',

      pacientes: [],
      casos: [],

      paciente: {
        nombre: '',
        apellido: '',
        identificacion: '',
        fecha_nacimiento: '',
        email: '',
        telefono: ''
      },

      caso: {
        id_paciente_fk: '',
        diagnostico: '',
        estado: 'abierto'
      },

      muestra: {
        id_caso_fk: '',
        tipo_muestra: 'saliva',
        ruta_imagen: null
      }
    };
  },

  mounted() {
    this.cargarPacientes();
    this.cargarCasos();
  },

  methods: {
    /* ================= PACIENTE ================= */
    async crearPaciente() {
      try {
        const res = await axios.post(`${this.API}/pacientes/`, this.paciente);
        console.log('Paciente creado:', res.data);
        alert('Paciente creado exitosamente');

        this.paciente = {
          nombre: '',
          apellido: '',
          identificacion: '',
          fecha_nacimiento: '',
          email: '',
          telefono: ''
        };

        await this.cargarPacientes();
        this.vistaActiva = 'caso';
      } catch (e) {
        console.error('Error completo:', e);
        console.error('Respuesta del servidor:', e.response?.data);
        alert('Error al crear paciente: ' + (e.response?.data?.error || e.message));
      }
    },

    async cargarPacientes() {
      try {
        const r = await axios.get(`${this.API}/pacientes/`);
        this.pacientes = r.data;
      } catch (e) {
        console.error('Error al cargar pacientes:', e);
      }
    },

    /* ================= CASO ================= */
    async crearCaso() {
      try {
        const res = await axios.post(`${this.API}/casos/`, this.caso);
        console.log('Caso creado:', res.data);
        alert('Caso clínico creado exitosamente');

        this.caso = {
          id_paciente_fk: '',
          diagnostico: '',
          estado: 'abierto'
        };

        await this.cargarCasos();
        this.vistaActiva = 'muestra';
      } catch (e) {
        console.error('Error completo:', e);
        console.error('Respuesta del servidor:', e.response?.data);
        alert('Error al crear caso: ' + (e.response?.data?.error || e.message));
      }
    },

    async cargarCasos() {
      try {
        const r = await axios.get(`${this.API}/casos/`);
        this.casos = r.data;
      } catch (e) {
        console.error('Error al cargar casos:', e);
      }
    },

    /* ================= MUESTRA ================= */
    onFile(e) {
      // CORREGIDO: nombre del método
      this.muestra.ruta_imagen = e.target.files[0];
      console.log('Archivo seleccionado:', this.muestra.ruta_imagen?.name);
    },

    async crearMuestra() {
      try {
        if (!this.muestra.ruta_imagen) {
          alert('Debe seleccionar una imagen');
          return;
        }

        const fd = new FormData();
        fd.append('id_caso_fk', this.muestra.id_caso_fk);
        fd.append('tipo_muestra', this.muestra.tipo_muestra);
        fd.append('ruta_imagen', this.muestra.ruta_imagen);

        console.log('Enviando muestra:', {
          id_caso_fk: this.muestra.id_caso_fk,
          tipo_muestra: this.muestra.tipo_muestra,
          archivo: this.muestra.ruta_imagen.name
        });

        const response = await axios.post(`${this.API}/subir-muestra/`, fd, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });

        console.log('Respuesta del servidor:', response.data);
        alert('Muestra creada exitosamente. Análisis en proceso.');

        this.muestra = {
          id_caso_fk: '',
          tipo_muestra: 'saliva',
          ruta_imagen: null
        };

        // Reiniciar el input de archivo
        const fileInput = document.querySelector('input[type="file"]');
        if (fileInput) fileInput.value = '';

      } catch (e) {
        console.error('Error completo:', e);
        console.error('Respuesta del servidor:', e.response?.data);
        alert('Error al crear muestra: ' + (e.response?.data?.error || e.response?.data?.detalle || e.message));
      }
    },

    /* ================= HELPERS ================= */
    getPacienteNombre(id_paciente) {
      const paciente = this.pacientes.find(p => p.id_paciente === id_paciente);
      return paciente ? `${paciente.nombre} ${paciente.apellido}` : 'Desconocido';
    }
  }
};
</script>

<style scoped>
/* =========================
   CONTENEDOR GENERAL
========================= */
.content {
  padding: 32px 20px;
  display: flex;
  justify-content: center;
}

/* CONTENEDOR CENTRAL */
.center-container {
  width: 100%;
  max-width: 1200px;
}

.page-header,
.tabs-container,
.form-wrapper {
  max-width: 100%;
}

/* =========================
   HEADER
========================= */
.page-header {
  max-width: 900px;
  margin: 0 auto 20px;
  display: flex;
  align-items: center;
}

.page-header h2 {
  font-size: 20px;
  font-weight: 600;
  color: #2c3e50;
}

.header-actions .btn-outline {
  border: 1px solid #ccc;
  background: white;
  padding: 8px 14px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s ease;
}

.header-actions .btn-outline:hover {
  background: #f5f7fa;
}

/* =========================
   TABS
========================= */
.tabs-container {
  max-width: 900px;
  margin: 0 auto 25px;
  display: flex;
  gap: 6px;
  border-bottom: 1px solid #e5e7eb;
}

.tab-btn {
  padding: 10px 18px;
  font-size: 13px;
  border: none;
  background: transparent;
  cursor: pointer;
  color: #6b7280;
  border-bottom: 3px solid transparent;
  transition: all 0.2s ease;
}

.tab-btn:hover {
  color: #374151;
}

.tab-btn.active {
  color: #4f46e5;
  font-weight: 600;
  border-bottom-color: #4f46e5;
}

/* =========================
   CARD
========================= */
.form-wrapper {
  max-width: 900px;
  margin: 0 auto;
  padding-top: 20px;
}

.card {
  background: #ffffff;
  border-radius: 14px;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

.card-header {
  position: relative;
  padding: 18px 22px;
  background: linear-gradient(135deg, #f9faff, #ffffff);
  border-bottom: 1px solid #e5e7eb;
}

.card-header::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  width: 4px;
  background: linear-gradient(180deg, #4f46e5, #6366f1);
  border-radius: 0 4px 4px 0;
}

.card-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
  color: #374151;
  letter-spacing: 0.2px;
}

.card-body {
  padding: 22px;
}

/* =========================
   FORMULARIOS
========================= */
.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 18px;
}

.form-grid input {
  padding: 11px 12px;
  border-radius: 8px;
  border: 1.8px solid #e5e7eb;
  font-size: 13px;
  transition: all 0.2s ease;
}

.form-grid input:focus {
  outline: none;
  border-color: #4f46e5;
  background: #f9faff;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 12px;
  font-weight: 600;
  color: #6b7280;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 11px 12px;
  border-radius: 8px;
  border: 1.8px solid #e5e7eb;
  font-size: 13px;
  transition: all 0.2s ease;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #4f46e5;
  background: #f9faff;
}

.form-group textarea {
  resize: vertical;
  font-family: inherit;
}

/* =========================
   ACCIONES
========================= */
.form-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 25px;
  padding-top: 18px;
  border-top: 1px solid #e5e7eb;
}

.btn-primary {
  background: #4f46e5;
  color: white;
  padding: 10px 22px;
  font-size: 13px;
  border-radius: 10px;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary:hover {
  background: #4338ca;
}

.btn-primary:disabled {
  background: #c7c7c7;
  cursor: not-allowed;
}

/* =========================
   RESPONSIVE
========================= */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .tabs-container {
    overflow-x: auto;
    white-space: nowrap;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .form-wrapper {
    padding-top: 10px;
  }

  .card-body {
    padding: 18px 16px;
  }

  .btn-primary {
    width: 100%;
    justify-content: center;
  }

  .form-actions {
    justify-content: stretch;
  }
}
</style>
