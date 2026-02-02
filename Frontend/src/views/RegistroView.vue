<template>
  <div class="content">
    
    <!-- HEADER -->
    <header class="page-header">
      <h2>Registro de Datos</h2>
      <div class="header-actions">
        <button class="btn-outline" @click="limpiarFormularioActivo">
          🗑️ Limpiar
        </button>
      </div>
    </header>

    <!-- TABS -->
    <div class="tabs-container">
      <button 
        class="tab-btn"
        :class="{ active: vistaActiva === 'paciente' }"
        @click="vistaActiva = 'paciente'"
      >
        Nuevo Paciente
      </button>
      <button 
        class="tab-btn"
        :class="{ active: vistaActiva === 'caso' }"
        @click="vistaActiva = 'caso'"
      >
        Nuevo Caso
      </button>
      <button 
        class="tab-btn"
        :class="{ active: vistaActiva === 'imagenes' }"
        @click="vistaActiva = 'imagenes'"
      >
        Agregar Imágenes
      </button>
    </div>

    <!-- CONTENIDO DE LOS TABS -->
    <div class="tab-content">

      <!-- ========== FORMULARIO NUEVO PACIENTE ========== -->
      <div v-if="vistaActiva === 'paciente'" class="form-wrapper">
        <div class="card">
          <div class="card-header">
            <h3>Datos del Paciente</h3>
          </div>
          
          <div class="card-body">
            <form @submit.prevent="crearPaciente">
              <div class="form-grid">
                <div class="form-group">
                  <label>Nombre *</label>
                  <input 
                    v-model="formPaciente.nombre" 
                    type="text" 
                    required
                    placeholder="Nombre"
                  />
                </div>

                <div class="form-group">
                  <label>Apellido *</label>
                  <input 
                    v-model="formPaciente.apellido" 
                    type="text" 
                    required
                    placeholder="Apellido"
                  />
                </div>

                <div class="form-group">
                  <label>Identificación *</label>
                  <input 
                    v-model="formPaciente.identificacion" 
                    type="text" 
                    required
                    placeholder="ID o Cédula"
                  />
                </div>

                <div class="form-group">
                  <label>Fecha de Nacimiento *</label>
                  <input 
                    v-model="formPaciente.fecha_nacimiento" 
                    type="date" 
                    required
                  />
                </div>

                <div class="form-group">
                  <label>Email</label>
                  <input 
                    v-model="formPaciente.email" 
                    type="email"
                    placeholder="correo@ejemplo.com"
                  />
                </div>

                <div class="form-group">
                  <label>Teléfono</label>
                  <input 
                    v-model="formPaciente.telefono" 
                    type="tel"
                    placeholder="3331234567"
                  />
                </div>
              </div>

              <div class="form-actions">
                <button type="submit" class="btn-primary">
                  ✓ Registrar Paciente
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>

      <!-- ========== FORMULARIO NUEVO CASO ========== -->
      <div v-if="vistaActiva === 'caso'" class="form-wrapper">
        <div class="card">
          <div class="card-header">
            <h3>Crear Nuevo Caso</h3>
          </div>
          
          <div class="card-body">
            <form @submit.prevent="crearCaso">
              <div class="form-group">
                <label>Seleccionar Paciente *</label>
                <select v-model="formCaso.paciente" required>
                  <option value="">-- Seleccione un paciente --</option>
                  <option 
                    v-for="paciente in pacientes" 
                    :key="paciente.id_paciente"
                    :value="paciente.id_paciente"
                  >
                    {{ paciente.nombre }} {{ paciente.apellido }} - {{ paciente.identificacion }}
                  </option>
                </select>
              </div>

              <div class="form-group">
                <label>Título del Caso *</label>
                <input 
                  v-model="formCaso.titulo" 
                  type="text" 
                  required
                  placeholder="Ej: Análisis de rutina - Enero 2026"
                />
              </div>

              <div class="form-group">
                <label>Descripción</label>
                <textarea 
                  v-model="formCaso.descripcion" 
                  rows="4"
                  placeholder="Detalles o notas sobre el caso..."
                ></textarea>
              </div>

              <div class="checkbox-wrapper">
                <input 
                  v-model="formCaso.crear_analisis" 
                  type="checkbox" 
                  id="crear_analisis"
                />
                <label for="crear_analisis">Crear análisis automáticamente</label>
              </div>

              <div class="form-actions">
                <button type="submit" class="btn-primary">
                  ✓ Crear Caso
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>

      <!-- ========== FORMULARIO AGREGAR IMÁGENES ========== -->
      <div v-if="vistaActiva === 'imagenes'" class="form-wrapper">
        <div class="card">
          <div class="card-header">
            <h3>Agregar Imágenes a Caso Existente</h3>
          </div>
          
          <div class="card-body">
            <form @submit.prevent="subirImagenes">
              <div class="form-group">
                <label>Seleccionar Paciente *</label>
                <select v-model="formImagenes.paciente" required @change="cargarCasosPaciente">
                  <option value="">-- Seleccione un paciente --</option>
                  <option 
                    v-for="paciente in pacientes" 
                    :key="paciente.id_paciente"
                    :value="paciente.id_paciente"
                  >
                    {{ paciente.nombre }} {{ paciente.apellido }}
                  </option>
                </select>
              </div>

              <div class="form-group" v-if="formImagenes.paciente">
                <label>Seleccionar Caso *</label>
                <select v-model="formImagenes.caso" required @change="cargarAnalisisCaso">
                  <option value="">-- Seleccione un caso --</option>
                  <option 
                    v-for="caso in casosDisponibles" 
                    :key="caso.id_caso"
                    :value="caso.id_caso"
                  >
                    {{ caso.titulo }}
                  </option>
                </select>
              </div>

              <div class="form-group" v-if="formImagenes.caso">
                <label>Seleccionar Análisis *</label>
                <select v-model="formImagenes.analisis" required>
                  <option value="">-- Seleccione un análisis --</option>
                  <option 
                    v-for="analisis in analisisDisponibles" 
                    :key="analisis.id_analisis"
                    :value="analisis.id_analisis"
                  >
                    Análisis #{{ analisis.id_analisis }} - {{ estadoTexto(analisis.estado) }}
                  </option>
                </select>
              </div>

              <div class="form-group" v-if="formImagenes.analisis">
                <label>Seleccionar Imágenes *</label>
                <input 
                  type="file" 
                  multiple 
                  accept="image/*"
                  @change="onFileChange"
                  ref="fileInput"
                  class="file-input"
                />
                <p class="help-text">Puede seleccionar múltiples imágenes</p>
              </div>

              <!-- PREVIEW DE IMÁGENES -->
              <div v-if="imagenesPreview.length > 0" class="preview-section">
                <label>Vista Previa ({{ imagenesPreview.length }} imagen{{ imagenesPreview.length > 1 ? 'es' : '' }})</label>
                <div class="preview-grid">
                  <div 
                    v-for="(img, index) in imagenesPreview" 
                    :key="index"
                    class="preview-item"
                  >
                    <img :src="img.url" :alt="`Preview ${index}`" />
                    <button 
                      type="button" 
                      class="remove-btn"
                      @click="removerImagen(index)"
                      title="Eliminar"
                    >
                      ✕
                    </button>
                  </div>
                </div>
              </div>

              <div class="form-actions">
                <button 
                  type="submit" 
                  class="btn-primary"
                  :disabled="imagenesPreview.length === 0"
                >
                  ⬆ Subir {{ imagenesPreview.length }} Imagen{{ imagenesPreview.length !== 1 ? 'es' : '' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>

    </div>

    <!-- NOTIFICACIÓN -->
    <transition name="notification-slide">
      <div v-if="notificacion.mostrar" class="notification" :class="notificacion.tipo">
        <span>{{ notificacion.mensaje }}</span>
        <button @click="notificacion.mostrar = false" class="notification-close">✕</button>
      </div>
    </transition>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'RegistroView',

  data() {
    return {
      API_URL: 'http://127.0.0.1:8000',
      vistaActiva: 'paciente',

      // Formulario Paciente
      formPaciente: {
        nombre: '',
        apellido: '',
        identificacion: '',
        fecha_nacimiento: '',
        email: '',
        telefono: ''
      },

      // Formulario Caso
      formCaso: {
        paciente: '',
        titulo: '',
        descripcion: '',
        crear_analisis: true
      },

      // Formulario Imágenes
      formImagenes: {
        paciente: '',
        caso: '',
        analisis: '',
        archivos: []
      },

      // Datos
      pacientes: [],
      casosDisponibles: [],
      analisisDisponibles: [],
      imagenesPreview: [],

      // Notificación
      notificacion: {
        mostrar: false,
        mensaje: '',
        tipo: 'success'
      }
    };
  },

  mounted() {
    this.cargarPacientes();
  },

  methods: {
    async cargarPacientes() {
      try {
        const response = await axios.get(`${this.API_URL}/api/pacientes/`);
        this.pacientes = response.data;
      } catch (error) {
        console.error('Error al cargar pacientes:', error);
        this.mostrarNotificacion('Error al cargar pacientes', 'error');
      }
    },

    async cargarCasosPaciente() {
      if (!this.formImagenes.paciente) return;
      
      try {
        const response = await axios.get(
          `${this.API_URL}/api/pacientes/${this.formImagenes.paciente}/casos/`
        );
        this.casosDisponibles = response.data;
        this.formImagenes.caso = '';
        this.formImagenes.analisis = '';
        this.analisisDisponibles = [];
      } catch (error) {
        console.error('Error al cargar casos:', error);
      }
    },

    async cargarAnalisisCaso() {
      if (!this.formImagenes.caso) return;
      
      try {
        const response = await axios.get(
          `${this.API_URL}/api/casos/${this.formImagenes.caso}/analisis/`
        );
        this.analisisDisponibles = response.data;
        this.formImagenes.analisis = '';
      } catch (error) {
        console.error('Error al cargar análisis:', error);
      }
    },

    async crearPaciente() {
      try {
        await axios.post(`${this.API_URL}/api/pacientes/`, this.formPaciente);
        this.mostrarNotificacion('Paciente registrado exitosamente', 'success');
        this.limpiarFormPaciente();
        this.cargarPacientes();
      } catch (error) {
        console.error('Error al crear paciente:', error);
        this.mostrarNotificacion('Error al registrar paciente', 'error');
      }
    },

    async crearCaso() {
      try {
        const response = await axios.post(`${this.API_URL}/api/casos/`, {
          paciente: this.formCaso.paciente,
          titulo: this.formCaso.titulo,
          descripcion: this.formCaso.descripcion
        });

        if (this.formCaso.crear_analisis) {
          await axios.post(`${this.API_URL}/api/analisis/`, {
            id_paciente_fk: this.formCaso.paciente,
            id_caso_fk: response.data.id_caso,
            estado: 0
          });
        }

        this.mostrarNotificacion('Caso creado exitosamente', 'success');
        this.limpiarFormCaso();
      } catch (error) {
        console.error('Error al crear caso:', error);
        this.mostrarNotificacion('Error al crear caso', 'error');
      }
    },

    async subirImagenes() {
      try {
        const promises = this.formImagenes.archivos.map(archivo => {
          const formData = new FormData();
          formData.append('imagen', archivo);
          formData.append('analisis', this.formImagenes.analisis);
          
          return axios.post(`${this.API_URL}/api/muestras/`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
          });
        });

        await Promise.all(promises);
        this.mostrarNotificacion(
          `${this.formImagenes.archivos.length} imagen(es) subida(s) exitosamente`,
          'success'
        );
        this.limpiarFormImagenes();
      } catch (error) {
        console.error('Error al subir imágenes:', error);
        this.mostrarNotificacion('Error al subir imágenes', 'error');
      }
    },

    onFileChange(event) {
      const archivos = Array.from(event.target.files);
      this.formImagenes.archivos = archivos;
      
      this.imagenesPreview = archivos.map(archivo => ({
        url: URL.createObjectURL(archivo),
        archivo
      }));
    },

    removerImagen(index) {
      this.imagenesPreview.splice(index, 1);
      this.formImagenes.archivos.splice(index, 1);
      
      if (this.$refs.fileInput && this.imagenesPreview.length === 0) {
        this.$refs.fileInput.value = '';
      }
    },

    estadoTexto(estado) {
      const estados = { 0: 'Abierto', 1: 'En Proceso', 2: 'Cerrado' };
      return estados[estado] || 'Desconocido';
    },

    mostrarNotificacion(mensaje, tipo = 'success') {
      this.notificacion.mensaje = mensaje;
      this.notificacion.tipo = tipo;
      this.notificacion.mostrar = true;
      
      setTimeout(() => {
        this.notificacion.mostrar = false;
      }, 4000);
    },

    limpiarFormularioActivo() {
      if (this.vistaActiva === 'paciente') {
        this.limpiarFormPaciente();
      } else if (this.vistaActiva === 'caso') {
        this.limpiarFormCaso();
      } else if (this.vistaActiva === 'imagenes') {
        this.limpiarFormImagenes();
      }
    },

    limpiarFormPaciente() {
      this.formPaciente = {
        nombre: '',
        apellido: '',
        identificacion: '',
        fecha_nacimiento: '',
        email: '',
        telefono: ''
      };
    },

    limpiarFormCaso() {
      this.formCaso = {
        paciente: '',
        titulo: '',
        descripcion: '',
        crear_analisis: true
      };
    },

    limpiarFormImagenes() {
      this.formImagenes = {
        paciente: '',
        caso: '',
        analisis: '',
        archivos: []
      };
      this.imagenesPreview = [];
      this.casosDisponibles = [];
      this.analisisDisponibles = [];
      if (this.$refs.fileInput) {
        this.$refs.fileInput.value = '';
      }
    }
  }
};
</script>

<style scoped>
/* =========================
   CONTENEDOR GENERAL
========================= */
.content {
  padding: 20px;
}

/* =========================
   HEADER
========================= */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
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
  display: flex;
  gap: 6px;
  border-bottom: 1px solid #e5e7eb;
  margin-bottom: 25px;
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
   CHECKBOX
========================= */
.checkbox-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 18px 0;
}

.checkbox-wrapper label {
  font-size: 13px;
  color: #374151;
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
   FILE INPUT
========================= */
.help-text {
  font-size: 11px;
  color: #9ca3af;
}

.file-input {
  cursor: 8px;
}

/* =========================
   PREVIEW IMÁGENES
========================= */
.preview-section {
  margin-top: 25px;
}

.preview-section label {
  font-size: 12px;
  font-weight: 600;
  color: #6b7280;
}

.preview-grid {
  margin-top: 12px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 14px;
}

.preview-item {
  position: relative;
  aspect-ratio: 1;
  border-radius: 10px;
  overflow: hidden;
  background: #f3f4f6;
  border: 2px solid #e5e7eb;
}

.preview-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.remove-btn {
  position: absolute;
  top: 6px;
  right: 6px;
  background: rgba(220, 38, 38, 0.9);
  color: white;
  border: none;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  font-size: 14px;
  cursor: pointer;
}

.remove-btn:hover {
  background: rgba(185, 28, 28, 0.95);
}

/* =========================
   NOTIFICACIÓN
========================= */
.notification {
  position: fixed;
  bottom: 20px;
  right: 20px;
  background: #16a34a;
  color: white;
  padding: 14px 18px;
  border-radius: 10px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.15);
  display: flex;
  gap: 15px;
  align-items: center;
  z-index: 1000;
}

.notification.error {
  background: #dc2626;
}

.notification-close {
  background: transparent;
  border: none;
  color: white;
  font-size: 18px;
  cursor: pointer;
}

/* =========================
   TRANSICIÓN
========================= */
.notification-slide-enter-active,
.notification-slide-leave-active {
  transition: all 0.3s ease;
}

.notification-slide-enter-from {
  transform: translateX(100%);
  opacity: 0;
}

.notification-slide-leave-to {
  transform: translateY(20px);
  opacity: 0;
}

/* =========================
   EXTRA – RESPONSIVE
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