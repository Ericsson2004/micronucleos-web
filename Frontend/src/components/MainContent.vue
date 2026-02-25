<template>
  <main class="content">
    <header class="page-header">
      <div class="header-left">
        <h2 class="page-title">Resultados del Análisis</h2>
        <div class="breadcrumb">
          <span v-if="patientId" class="breadcrumb-item">
            <svg class="breadcrumb-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
              <circle cx="12" cy="7" r="4"></circle>
            </svg>
            Paciente {{ patientId }}
          </span>

          <span v-if="caseId" class="breadcrumb-separator">›</span>

          <span v-if="caseId" class="breadcrumb-item active">
            <svg class="breadcrumb-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path>
              <rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect>
            </svg>
            Caso {{ caseId }}
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
      <div class="gallery-column">
        <div class="gallery-header">
          <h3>Galería</h3>
          <span class="gallery-count">{{ totalImagenes }}</span>
        </div>

        <div class="gallery-section">
          <div class="gallery-toggle" @click="mostrarSegmentadas = !mostrarSegmentadas">
            <h4>Segmentadas</h4>
            <span class="section-count">
              {{ imagenesSegmentadas.length }}
            </span>
          </div>

          <div v-show="mostrarSegmentadas" class="gallery-grid">
            <div
              v-for="muestra in imagenesSegmentadas"
              :key="'seg-' + muestra.id_muestra"
              class="thumb"
              :class="{ active: muestra === imagenSeleccionada }"
              @click="imagenSeleccionada = muestra"
            >
              <img :src="muestra.imagen_thumbnail" loading="lazy" />
              <div class="thumb-overlay">
                <span class="thumb-id">#{{ muestra.id_muestra }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="gallery-section">
          <div class="gallery-toggle" @click="mostrarNoSegmentadas = !mostrarNoSegmentadas">
            <h4>No segmentadas</h4>
            <span class="section-count original">
              {{ imagenesNoSegmentadas.length }}
            </span>
          </div>

          <div v-show="mostrarNoSegmentadas" class="gallery-grid">
            <div
              v-for="muestra in imagenesNoSegmentadas"
              :key="'no-' + muestra.id_muestra"
              class="thumb"
              :class="{ active: muestra === imagenSeleccionada }"
              @click="imagenSeleccionada = muestra"
            >
              <img :src="muestra.imagen_thumbnail" loading="lazy" />
              <div class="thumb-overlay">
                <span class="thumb-id">#{{ muestra.id_muestra }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="viewer-column">
        <div class="card main-card">
          <div class="card-body split-view">
            <div class="image-container">
              <div class="img-placeholder">
                <img
                  v-if="imagenSeleccionada"
                  :src="imagenSeleccionada.imagen_original"
                  class="main-image clickable"
                  alt="Muestra microscópica"
                  @click="imagenEnEdicion = true"
                />

                <img
                  v-if="imagenSeleccionada && verMascara && imagenSeleccionada.id_analisis"
                  :key="`mask-${imagenSeleccionada.id_analisis}-${mascaraActual}`"
                  :src="obtenerUrlMascara()"
                  class="mask-overlay"
                  alt="Máscaras"
                  @error="handleMascaraError"
                />

                <div v-if="!imagenSeleccionada" class="empty-image-state">
                  <div class="empty-image-icon">🔬</div>
                  <p>Seleccione una imagen de la galería</p>
                </div>

                <div v-if="imagenSeleccionada" class="img-overlay">
                  <button
                    v-if="imagenSeleccionada.id_analisis"
                    class="seg-toggle"
                    :class="{ active: verMascara }"
                    @click="toggleTodasMascaras"
                    :title="verMascara ? 'Ocultar segmentación' : 'Ver segmentación'"
                  >
                    <svg
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    >
                      <path
                        v-if="verMascara"
                        d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24M1 1l22 22"
                      />
                      <template v-else>
                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                        <circle cx="12" cy="12" r="3" />
                      </template>
                    </svg>
                    <span>{{ verMascara ? "Ocultar" : "Segmentación" }}</span>
                  </button>
                  <span v-else class="no-seg-badge">Sin segmentar</span>
                </div>
              </div>
            </div>

            <div class="data-container">
              <div class="card-header">
                <div class="card-title-section">
                  <h3>
                    {{
                      imagenSeleccionada
                        ? "Muestra #" + imagenSeleccionada.id_muestra
                        : "Vista previa"
                    }}
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
                      <div class="structure-cell">
                        <svg class="table-icon" viewBox="0 0 24 24" fill="none" stroke="#1e88e5" stroke-width="2">
                          <circle cx="12" cy="12" r="8" />
                          <circle cx="12" cy="12" r="3" fill="#1e88e5" stroke="none" />
                        </svg>
                        <span>Núcleos</span>
                      </div>
                    </td>
                    <td class="count">{{ resultadoImagenSeleccionada.nucleos }}</td>
                  </tr>
                  <tr class="data-row membranas">
                    <td>
                      <div class="structure-cell">
                        <svg class="table-icon" viewBox="0 0 24 24" fill="none" stroke="#4caf50" stroke-width="2">
                          <circle cx="12" cy="12" r="7" stroke-dasharray="3 3"/>
                          <circle cx="12" cy="12" r="3" />
                        </svg>
                        <span>Membranas</span>
                      </div>
                    </td>
                    <td class="count">{{ resultadoImagenSeleccionada.membranas }}</td>
                  </tr>
                  <tr class="data-row micronucleos highlight">
                    <td>
                      <div class="structure-cell">
                        <svg class="table-icon" viewBox="0 0 24 24" fill="none" stroke="#ab47bc" stroke-width="2">
                          <circle cx="12" cy="12" r="6" />
                          <circle cx="12" cy="12" r="2" fill="#ab47bc" stroke="none" />
                        </svg>
                        <span>Micronúcleos</span>
                      </div>
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
                      <input
                        type="checkbox"
                        class="checkbox-custom"
                        v-model="mascarasVisibles.nucleo"
                        @change="actualizarMascara"
                      />
                    </td>
                    <td class="obj-type">
                      <span class="obj-icon nucleos">
                        <svg class="elegant-icon" viewBox="0 0 24 24" fill="none" stroke="#64b5f6" stroke-width="1.5">
                          <circle cx="12" cy="12" r="8" />
                          <circle cx="12" cy="12" r="3" fill="#1e88e5" stroke="none" />
                        </svg>
                      </span>
                      Núcleos
                    </td>
                    <td>
                      <div class="obj-actions">
                        <button
                          class="obj-btn"
                          @click="verMascaraSola('nucleo')"
                          title="Ver solo esta máscara"
                        >
                          👁️
                        </button>
                        <button class="obj-btn" title="Editar">✏️</button>
                      </div>
                    </td>
                  </tr>

                  <tr class="obj-row">
                    <td>
                      <input
                        type="checkbox"
                        class="checkbox-custom"
                        v-model="mascarasVisibles.micronucleo"
                        @change="actualizarMascara"
                      />
                    </td>
                    <td class="obj-type">
                      <span class="obj-icon micronucleos">
                        <svg class="elegant-icon" viewBox="0 0 24 24" fill="none" stroke="#ba68c8" stroke-width="1.5">
                          <circle cx="12" cy="12" r="5" />
                          <circle cx="12" cy="12" r="1.5" fill="#8e24aa" stroke="none" />
                        </svg>
                      </span>
                      Micronúcleos
                    </td>
                    <td>
                      <div class="obj-actions">
                        <button
                          class="obj-btn"
                          @click="verMascaraSola('micronucleo')"
                          title="Ver solo esta máscara"
                        >
                          👁️
                        </button>
                        <button class="obj-btn" title="Editar">✏️</button>
                      </div>
                    </td>
                  </tr>

                  <tr class="obj-row">
                    <td>
                      <input
                        type="checkbox"
                        class="checkbox-custom"
                        v-model="mascarasVisibles.membrana"
                        @change="actualizarMascara"
                      />
                    </td>
                    <td class="obj-type">
                      <svg class="elegant-icon" viewBox="0 0 24 24" fill="none" stroke="#4caf50" stroke-width="1.5">
                        <path d="M4 12c0-4.418 3.582-8 8-8s8 3.582 8 8-3.582 8-8 8-8-3.582-8-8z" stroke-dasharray="3 3" />
                        <circle cx="12" cy="12" r="5" stroke="#4caf50" />
                      </svg>
                      Membranas
                    </td>
                    <td>
                      <div class="obj-actions">
                        <button
                          class="obj-btn"
                          @click="verMascaraSola('membrana')"
                          title="Ver solo esta máscara"
                        >
                          👁️
                        </button>
                        <button class="obj-btn" title="Editar">✏️</button>
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

  <div v-if="imagenEnEdicion" class="image-editor-overlay" @click.self="cerrarEditor">
    <div class="editor-container">
      <button class="close-btn" @click="cerrarEditor">✖</button>

      <div class="editor-layout">
        <!-- PANEL LATERAL -->
        <div class="editor-sidebar">
          <!-- SEPARADOR: VISIBILIDAD DE MASCARAS -->
          <div class="editor-section-label">Visibilidad</div>

          <button
            class="tool-option"
            :class="{
              'active overlay-active': editorVerMascara && editorMascaraActual === 'overlay',
            }"
            @click="editorToggleMascara('overlay')"
            :title="
              editorVerMascara && editorMascaraActual === 'overlay' ? 'Ocultar todas' : 'Ver todas'
            "
          >
            <svg
              class="elegant-icon"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#90caf9"
              stroke-width="1.5"
            >
              <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
              <circle cx="12" cy="12" r="3" />
            </svg>
            <span>Todas</span>
          </button>

          <button
            class="tool-option"
            :class="{
              'active membrana-active': editorVerMascara && editorMascaraActual === 'membrana',
            }"
            @click="editorToggleMascara('membrana')"
          >
            <svg
              class="elegant-icon"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#4caf50"
              stroke-width="1.5"
            >
              <path
                d="M4 12c0-4.418 3.582-8 8-8s8 3.582 8 8-3.582 8-8 8-8-3.582-8-8z"
                stroke-dasharray="3 3"
              />
              <circle cx="12" cy="12" r="5" stroke="#4caf50" />
            </svg>
            <span>Membrana</span>
          </button>

          <button
            class="tool-option"
            :class="{
              'active nucleo-active': editorVerMascara && editorMascaraActual === 'nucleo',
            }"
            @click="editorToggleMascara('nucleo')"
          >
            <svg
              class="elegant-icon"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#64b5f6"
              stroke-width="1.5"
            >
              <circle cx="12" cy="12" r="8" />
              <circle cx="12" cy="12" r="3" fill="#1e88e5" stroke="none" />
            </svg>
            <span>Núcleo</span>
          </button>

          <button
            class="tool-option"
            :class="{
              'active micronucleo-active':
                editorVerMascara && editorMascaraActual === 'micronucleo',
            }"
            @click="editorToggleMascara('micronucleo')"
          >
            <svg
              class="elegant-icon"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#ba68c8"
              stroke-width="1.5"
            >
              <circle cx="12" cy="12" r="5" />
              <circle cx="12" cy="12" r="1.5" fill="#8e24aa" stroke="none" />
            </svg>
            <span>Micronúcleo</span>
          </button>

          <!-- SEPARADOR: INFO -->
          <div class="editor-section-label" style="margin-top: 8px">Info</div>
          <div class="editor-info" v-if="resultadoImagenSeleccionada">
            <div class="editor-info-row nucleo-color">
              <span class="editor-dot" style="background: #00dc00"></span>
              <span>{{ resultadoImagenSeleccionada.nucleos }} núcleos</span>
            </div>
            <div class="editor-info-row micronucleo-color">
              <span class="editor-dot" style="background: #ff0000"></span>
              <span>{{ resultadoImagenSeleccionada.micronucleos }} micronúcleos</span>
            </div>
            <div class="editor-info-row membrana-color">
              <span class="editor-dot" style="background: #0078ff"></span>
              <span>{{ resultadoImagenSeleccionada.membranas }} membranas</span>
            </div>
          </div>
          <div class="editor-info" v-else>
            <span class="editor-no-data">Sin análisis</span>
          </div>
        </div>

        <!-- IMAGEN + MASCARA + FLECHAS -->
        <div ref="editorWrapper" class="editor-image-wrapper" @wheel.prevent="onWheelZoom">
          <!-- Imagen original -->
          <img
            ref="editorImage"
            :src="imagenSeleccionada.imagen_original"
            class="editor-image"
            alt="Imagen en edición"
            @dblclick.stop="resetZoom"
            @mousedown.prevent.stop="startDrag"
            @mousemove.prevent.stop="onDrag"
            @mouseup.prevent.stop="endDrag"
            @mouseleave="endDrag"
            :style="{
              transform: `translate(${offsetX}px, ${offsetY}px) scale(${zoom})`,
              cursor: zoom > 1 ? (isDragging ? 'grabbing' : 'grab') : 'zoom-in',
            }"
          />

          <!-- Mascara superpuesta — misma transformacion que la imagen -->
          <img
            v-if="editorVerMascara && imagenSeleccionada.id_analisis"
            :key="`editor-mask-${imagenSeleccionada.id_analisis}-${editorMascaraActual}`"
            :src="obtenerUrlMascaraEditor()"
            class="editor-mask-overlay"
            alt="Mascara"
            :style="{
              transform: `translate(${offsetX}px, ${offsetY}px) scale(${zoom})`,
            }"
            @error="editorVerMascara = false"
          />

          <!-- FLECHAS -->
          <button
            class="nav-arrow left"
            @click.stop="imagenAnterior"
            :disabled="indiceImagenSeleccionada <= 0"
          >
            ‹
          </button>

          <button
            class="nav-arrow right"
            @click.stop="siguienteImagen"
            :disabled="indiceImagenSeleccionada >= imagenes.length - 1"
          >
            ›
          </button>

          <!-- ZOOM INDICATOR -->
          <div v-if="zoom > 1" class="zoom-indicator">{{ Math.round(zoom * 100) }}%</div>
        </div>
        <!-- PANEL DERECHO - EDICIÓN -->
        <div class="editor-sidebar editor-sidebar-right">

          <div class="editor-section-label">Edición</div>

          <!-- Edición Activa / Inactiva -->
          <button
            class="tool-option"
            :class="{ 'active modo-edicion-active': edicionActiva }"
            @click="edicionActiva = !edicionActiva"
          >
            <svg v-if="edicionActiva" class="elegant-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
              <path d="M7 11V7a5 5 0 0 1 9.9-1"></path> </svg>

            <svg v-else class="elegant-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
              <path d="M7 11V7a5 5 0 0 1 10 0v4"></path> </svg>

            <span>{{ edicionActiva ? "Edición Activa" : "Edición Inactiva" }}</span>
          </button>

          <!-- Agregar Membrana -->
          <button
            class="tool-option"
            :class="{ 'active membrana-active': herramientaActiva === 'agregar-membrana' && edicionActiva }"
            :disabled="!edicionActiva"
            @click="herramientaActiva = herramientaActiva === 'agregar-membrana' ? null : 'agregar-membrana'"
          >
            <svg class="elegant-icon" viewBox="0 0 24 24" fill="none" stroke="#4caf50" stroke-width="1.5">
              <path d="M4 12c0-4.418 3.582-8 8-8s8 3.582 8 8-3.582 8-8 8-8-3.582-8-8z" stroke-dasharray="3 3" />
              <circle cx="12" cy="12" r="5" stroke="#4caf50" />
            </svg>
            <span>Agregar Membrana</span>
          </button>

          <!-- Agregar Núcleo -->
          <button
            class="tool-option"
            :class="{ 'active nucleo-active': herramientaActiva === 'agregar-nucleo' && edicionActiva }"
            :disabled="!edicionActiva"
            @click="herramientaActiva = herramientaActiva === 'agregar-nucleo' ? null : 'agregar-nucleo'"
          >
            <svg class="elegant-icon" viewBox="0 0 24 24" fill="none" stroke="#64b5f6" stroke-width="1.5">
              <circle cx="12" cy="12" r="8" />
              <circle cx="12" cy="12" r="3" fill="#1e88e5" stroke="none" />
            </svg>
            <span>Agregar Núcleo</span>
          </button>

          <!-- Agregar Micronúcleo -->
          <button
            class="tool-option"
            :class="{ 'active micronucleo-active': herramientaActiva === 'agregar-micronucleo' && edicionActiva }"
            :disabled="!edicionActiva"
            @click="herramientaActiva = herramientaActiva === 'agregar-micronucleo' ? null : 'agregar-micronucleo'"
          >
            <svg class="elegant-icon" viewBox="0 0 24 24" fill="none" stroke="#ba68c8" stroke-width="1.5">
              <circle cx="12" cy="12" r="5" />
              <circle cx="12" cy="12" r="1.5" fill="#8e24aa" stroke="none" />
            </svg>
            <span>Agregar Micronúcleo</span>
          </button>

          <!-- Borrar -->
          <button
            class="tool-option danger"
            :class="{ 'active borrar-active': herramientaActiva === 'borrar' && edicionActiva }"
            :disabled="!edicionActiva"
            @click="herramientaActiva = herramientaActiva === 'borrar' ? null : 'borrar'"
          >
            <svg class="elegant-icon" viewBox="0 0 24 24" fill="none" stroke="#e0e0e0" stroke-width="1.5">
              <path d="M2.5 13.5l6-6a2.828 2.828 0 014 0l7 7a2.828 2.828 0 010 4h-11l-6-5z" />
              <path d="M12.5 10.5l-6 6" />
            </svg>
            <span>Borrar</span>
          </button>

          <!-- Editar -->
          <button
            class="tool-option"
            :class="{ 'active editar-active': herramientaActiva === 'editar' && edicionActiva }"
            :disabled="!edicionActiva"
            @click="herramientaActiva = herramientaActiva === 'editar' ? null : 'editar'"
          >
            <svg class="elegant-icon" viewBox="0 0 24 24" fill="none" stroke="#b388ff" stroke-width="1.5">
              <path d="M12 20h9" />
              <path d="M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4L16.5 3.5z" />
            </svg>
            <span>Editar</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "MainContent",

  props: {
    patientId: [String, Number],
    caseId: [String, Number],
    refreshKey: { type: Number, default: 0 },
  },

  data() {
    return {
      API_URL: "http://127.0.0.1:8000/api",
      BASE_MEDIA_URL: "http://127.0.0.1:8000",

      analisis: [],
      loading: false,
      imagenSeleccionada: null,
      imagenEnEdicion: false,
      verMascara: false,

      // Estado de mascara en el editor (independiente de la vista principal)
      editorVerMascara: false,
      editorMascaraActual: "overlay",

      // Estado del editor
      edicionActiva: false,

      // ⭐ Control de máscaras
      mascarasVisibles: {
        nucleo: true,
        micronucleo: true,
        membrana: true,
      },
      mascaraActual: "overlay", // 'overlay', 'nucleo', 'micronucleo', 'membrana'

      // Zoom y navegación
      zoom: 1,
      zoomMin: 1,
      zoomMax: 4,
      zoomStep: 0.15,
      offsetX: 0,
      offsetY: 0,

      isDragging: false,
      startX: 0,
      startY: 0,

      herramientaActiva: "editar",

      // Galeria
      muestras: [],
      mostrarSegmentadas: false,
      mostrarNoSegmentadas: false,
    };
  },

  computed: {
    imagenes() {
      return this.analisis.map((a) => {
        return {
          id_muestra: a.id_muestra_fk.id_muestra,
          id_analisis: a.id_analisis,

          imagen_thumbnail: `${this.BASE_MEDIA_URL}${a.id_muestra_fk.thumbnail}`,
          imagen_original: `${this.BASE_MEDIA_URL}${a.id_muestra_fk.ruta_imagen}`,

          tipo: a.id_muestra_fk.tipo_muestra,
          fecha: a.id_muestra_fk.fecha_toma,
          analisis_full: a,
        };
      });
    },

    imagenesSegmentadas() {
      return this.imagenes;
    },

    imagenesNoSegmentadas() {
      const idsAnalizados = this.analisis.map((a) => a.id_muestra_fk.id_muestra);

      return this.muestras
        .filter((m) => !idsAnalizados.includes(m.id_muestra))
        .map((m) => ({
          id_muestra: m.id_muestra,
          id_analisis: null,
          imagen_thumbnail: `${this.BASE_MEDIA_URL}${m.thumbnail}`,
          imagen_original: `${this.BASE_MEDIA_URL}${m.ruta_imagen}`,
          tipo: m.tipo_muestra,
          fecha: m.fecha_toma,
          analisis_full: null,
        }));
    },

    totalImagenes() {
      return this.imagenesSegmentadas.length + this.imagenesNoSegmentadas.length;
    },

    resultadoImagenSeleccionada() {
      const analisis = this.imagenSeleccionada?.analisis_full;
      if (!analisis) return null;

      // Prioridad 1: resultados tipados del modelo AnalisisResultados
      if (analisis.resultados) {
        return {
          nucleos: analisis.resultados.total_nucleos,
          membranas: analisis.resultados.total_membranas,
          micronucleos: analisis.resultados.total_micronucleos,
        };
      }

      // Prioridad 2: contenido_json del archivo activo (fallback)
      const archivoActivo = analisis.archivos?.find((a) => a.activo);
      if (!archivoActivo?.contenido_json) return null;

      const json = archivoActivo.contenido_json;
      const objetos = json.objetos ?? [];

      return {
        nucleos: objetos.filter((o) => o.tipo === "nucleo").length,
        membranas: objetos.filter((o) => o.tipo === "membrana").length,
        micronucleos: objetos.filter((o) => o.tipo === "micronucleo").length,
      };
    },

    indiceImagenSeleccionada() {
      if (!this.imagenSeleccionada) return -1;
      return this.imagenes.findIndex((i) => i.id_muestra === this.imagenSeleccionada.id_muestra);
    },
  },

  watch: {
    // Recargar cuando el Sidebar notifica progreso o completado
    refreshKey(newVal, oldVal) {
      if (newVal !== oldVal && this.caseId) {
        this.$options.watch.caseId.handler.call(this, this.caseId);
      }
    },

    // Al cambiar imagen: si la nueva no tiene análisis, ocultar máscara.
    // Si tiene análisis y verMascara estaba activo, mantenerlo.
    imagenSeleccionada(nueva) {
      if (!nueva || !nueva.id_analisis) {
        this.verMascara = false;
      }
      // Resetear siempre al overlay completo al cambiar imagen
      this.mascarasVisibles = { nucleo: true, micronucleo: true, membrana: true };
      this.mascaraActual = "overlay";
    },

    caseId: {
      immediate: true,
      async handler(id) {
        if (!id) {
          this.analisis = [];
          this.muestras = [];
          this.imagenSeleccionada = null;
          this.verMascara = false;
          return;
        }

        this.loading = true;

        try {
          // 🔹 1️⃣ Cargar análisis (segmentadas)
          console.log("Cargando análisis desde:", `${this.API_URL}/casos/${id}/analisis/`);
          const res = await axios.get(`${this.API_URL}/casos/${id}/analisis/`);

          this.analisis = res.data;
          console.log("Análisis cargados:", this.analisis.length);

          // 🔹 2️⃣ Cargar muestras (todas las imágenes del caso)
          console.log("Cargando muestras desde:", `${this.API_URL}/casos/${id}/muestras/`);
          const resMuestras = await axios.get(`${this.API_URL}/casos/${id}/muestras/`);
          this.muestras = resMuestras.data;

          // 🔹 3️⃣ Seleccionar primera imagen (segmentada si existe)
          if (this.imagenesSegmentadas.length > 0) {
            this.imagenSeleccionada = this.imagenesSegmentadas[0];
          } else if (this.imagenesNoSegmentadas.length > 0) {
            this.imagenSeleccionada = this.imagenesNoSegmentadas[0];
          } else {
            this.imagenSeleccionada = null;
          }
        } catch (e) {
          console.error("❌ Error cargando datos:", e);
          console.error("❌ URL que falló:", e.config?.url);
        } finally {
          this.loading = false;
        }
      },
    },
  },

  mounted() {
    window.addEventListener("keydown", this.teclasOverlay);
  },

  beforeUnmount() {
    window.removeEventListener("keydown", this.teclasOverlay);
  },

  methods: {
    // ============================================================
    // NAVEGACIÓN DE IMÁGENES
    // ============================================================
    siguienteImagen() {
      if (this.indiceImagenSeleccionada < this.imagenes.length - 1) {
        this.imagenSeleccionada = this.imagenes[this.indiceImagenSeleccionada + 1];
      }
    },

    imagenAnterior() {
      if (this.indiceImagenSeleccionada > 0) {
        this.imagenSeleccionada = this.imagenes[this.indiceImagenSeleccionada - 1];
      }
    },

    teclasOverlay(e) {
      if (!this.imagenEnEdicion) return;
      if (e.key === "ArrowRight") this.siguienteImagen();
      if (e.key === "ArrowLeft") this.imagenAnterior();
      if (e.key === "Escape") this.imagenEnEdicion = false;
    },

    // ============================================================
    // ZOOM Y ARRASTRE
    // ============================================================
    onWheelZoom(e) {
      const zoomAnterior = this.zoom;

      // Calcular nuevo zoom
      if (e.deltaY < 0 && this.zoom < this.zoomMax) {
        this.zoom += this.zoomStep;
      }
      if (e.deltaY > 0 && this.zoom > this.zoomMin) {
        this.zoom -= this.zoomStep;
      }

      // Si no cambió, salir
      if (this.zoom === zoomAnterior) return;

      // Posición del mouse en el contenedor
      const rect = e.currentTarget.getBoundingClientRect();
      const mouseX = e.clientX - rect.left;
      const mouseY = e.clientY - rect.top;

      // Centro del contenedor
      const centerX = rect.width / 2;
      const centerY = rect.height / 2;

      // Distancia del mouse al centro
      const dx = mouseX - centerX;
      const dy = mouseY - centerY;

      // Ajuste por cambio de escala
      const factor = this.zoom / zoomAnterior;

      this.offsetX -= dx * (factor - 1);
      this.offsetY -= dy * (factor - 1);

      // Reset cuando vuelve a zoom normal
      if (this.zoom === 1) {
        this.offsetX = 0;
        this.offsetY = 0;
      }
      this.limitarMovimiento();
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

      this.limitarMovimiento();
    },

    endDrag() {
      this.isDragging = false;
    },

    limitarMovimiento() {
      // Eliminamos this.$nextTick para que el cálculo sea instantáneo y no vibre
      const wrapper = this.$refs.editorWrapper;
      const img = this.$refs.editorImage;

      if (!wrapper || !img) return;

      const wrapperRect = wrapper.getBoundingClientRect();

      // --- CAMBIO IMPORTANTE AQUÍ ---
      // Cambiamos 'naturalWidth' por 'offsetWidth' para usar el tamaño real visual
      // en lugar del tamaño original del archivo.
      const imgWidth = img.offsetWidth * this.zoom;
      const imgHeight = img.offsetHeight * this.zoom;

      // Calculamos los límites. Si la imagen (con zoom) es más chica que el contenedor,
      // maxX será 0, lo que impide que se mueva y la mantiene centrada.
      const maxX = imgWidth > wrapperRect.width ? (imgWidth - wrapperRect.width) / 2 : 0;
      const maxY = imgHeight > wrapperRect.height ? (imgHeight - wrapperRect.height) / 2 : 0;

      // Aplicamos la restricción matemática
      this.offsetX = Math.min(maxX, Math.max(-maxX, this.offsetX));
      this.offsetY = Math.min(maxY, Math.max(-maxY, this.offsetY));
    },

    // ============================================================
    // CONTROL DE MÁSCARAS
    // ============================================================

    /**
     * Ver solo una máscara específica (oculta las demás)
     */
    verMascaraSola(tipo) {
      this.mascaraActual = tipo;
      this.verMascara = true;

      // Desactivar checkboxes de las otras
      this.mascarasVisibles = {
        nucleo: tipo === "nucleo",
        micronucleo: tipo === "micronucleo",
        membrana: tipo === "membrana",
      };

      console.log(`👁️ Mostrando solo máscara: ${tipo}`);
    },

    /**
     * Actualizar overlay cuando cambian los checkboxes
     */
    actualizarMascara() {
      const activas = Object.values(this.mascarasVisibles).filter((v) => v).length;

      if (activas === 0) {
        // Si desactivan todas, ocultar máscaras
        this.verMascara = false;
        console.log("🚫 Máscaras ocultas");
      } else if (activas === 1) {
        // Si solo hay una activa, mostrar esa
        const tipoActivo = Object.keys(this.mascarasVisibles).find(
          (key) => this.mascarasVisibles[key],
        );
        this.mascaraActual = tipoActivo;
        this.verMascara = true;
        console.log(`👁️ Mostrando máscara: ${tipoActivo}`);
      } else {
        // Si hay varias, mostrar overlay combinado
        this.mascaraActual = "overlay";
        this.verMascara = true;
        console.log("🎨 Mostrando overlay combinado");
      }
    },

    /**
     * Toggle para mostrar/ocultar todas las máscaras
     */
    toggleTodasMascaras() {
      this.verMascara = !this.verMascara;

      if (this.verMascara) {
        // Activar todas
        this.mascarasVisibles = {
          nucleo: true,
          micronucleo: true,
          membrana: true,
        };
        this.mascaraActual = "overlay";
        console.log("Mostrando todas las máscaras");
      } else {
        // Ocultar pero mantener estado
        console.log("Ocultando máscaras");
      }
    },

    /**
     * Obtener URL de la máscara actual.
     * El backend acepta: nucleo | micronucleo | membrana | overlay
     * - Si hay varias activas → overlay (backend las combina)
     * - Si hay una sola activa → esa específica
     * - Si no hay ninguna   → "" (el template no muestra el <img>)
     */
    obtenerUrlMascara() {
      if (!this.imagenSeleccionada?.id_analisis) return "";

      const tipoUrl = this.mascaraActual; // ya lo gestiona actualizarMascara()
      if (!tipoUrl) return "";

      // Cache-buster para forzar recarga del PNG cuando cambia el tipo
      const url = `${this.API_URL}/mascaras/${this.imagenSeleccionada.id_analisis}/${tipoUrl}/?t=${tipoUrl}`;
      console.log("🖼️ URL de máscara:", url);
      return url;
    },

    /**
     * Manejo de errores al cargar máscara
     */
    handleMascaraError(event) {
      console.error("Error cargando mascara:", event.target?.src);
      this.verMascara = false;
    },

    // ── Editor methods ──────────────────────────────────────────────────

    cerrarEditor() {
      this.imagenEnEdicion = false;
      // Resetear zoom al cerrar
      this.zoom = 1;
      this.offsetX = 0;
      this.offsetY = 0;
    },

    editorToggleMascara(tipo) {
      // Si ya esta activo ese tipo, apagar. Si no, activar ese tipo.
      if (this.editorVerMascara && this.editorMascaraActual === tipo) {
        this.editorVerMascara = false;
      } else {
        this.editorVerMascara = true;
        this.editorMascaraActual = tipo;
      }
    },

    obtenerUrlMascaraEditor() {
      if (!this.imagenSeleccionada?.id_analisis) return "";
      return `${this.API_URL}/mascaras/${this.imagenSeleccionada.id_analisis}/${this.editorMascaraActual}/?t=${this.editorMascaraActual}`;
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
  display: flex;
  align-items: center;
  gap: 6px;
  color: #666;
  padding: 6px 12px;
  background: #f0f4f8;
  border-radius: 8px;
  font-weight: 500;
}

.breadcrumb-item.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.breadcrumb-separator {
  color: #999;
}

.breadcrumb-icon {
  width: 14px;
  height: 14px;
  opacity: 0.8;

}

.breadcrumb-separator {
  color: #999;
  font-size: 16px;
  font-weight: 600;
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
  width: 200px;
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
  background: linear-gradient(to top, rgba(0, 0, 0, 0.7), transparent);
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
/* Nuevo Galeria */
.gallery-section {
  margin-bottom: 12px;
}

.gallery-toggle {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  padding: 6px 8px;
  background: #f0f4f8;
  border-radius: 8px;
  margin-bottom: 6px;
  font-size: 12px;
  font-weight: 600;
  transition: background 0.2s ease;
}

.gallery-toggle:hover {
  background: #e2e8f0;
}

.section-count {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  min-width: 22px;
  text-align: center;
  transition: all 0.2s ease;
}

.section-count.original {
  background: linear-gradient(135deg, #42a5f5 0%, #1e88e5 100%);
}

.gallery-toggle:hover .section-count {
  transform: scale(1.1);
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

/* ============================================ */
/* VISTA DIVIDIDA */
/* ============================================ */

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

/* ============================================ */
/* CONTENEDOR DE IMAGEN Y OVERLAY DE MÁSCARAS */
/* ============================================ */

.img-placeholder {
  position: relative; /* ⭐ CRÍTICO */
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
  border-radius: 12px;
  overflow: hidden;
}

/* Imagen principal */
.main-image {
  max-width: 100%;
  max-height: 100%;
  width: auto;
  height: auto;
  object-fit: contain;
  display: block;
  position: relative;
  z-index: 1; /* Imagen en capa base */
}

/* ⭐ OVERLAY DE MÁSCARAS - POSICIÓN ABSOLUTA SOBRE LA IMAGEN */
.mask-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  max-width: 100%;
  max-height: 100%;
  width: auto;
  height: auto;
  object-fit: contain;
  pointer-events: none; /* Los clicks pasan a través del overlay */
  z-index: 2; /* Máscara encima de la imagen */
  opacity: 0.85; /* Semi-transparente para ver ambas capas */
  transition: opacity 0.3s ease;
}

.mask-overlay:hover {
  opacity: 1; /* Más opaca al pasar el mouse */
}

/* Estados de carga de la máscara */
.mask-overlay[src=""],
.mask-overlay:not([src]) {
  display: none; /* Ocultar si no hay src */
}

/* Estado vacío cuando no hay imagen */
.empty-image-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
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

/* ⭐ TOGGLE DE SEGMENTACIÓN — esquina inferior derecha, no tapa la imagen */
.img-overlay {
  position: absolute;
  bottom: 12px;
  right: 12px;
  z-index: 10;
  pointer-events: none;
}

.seg-toggle {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 7px 14px 7px 10px;
  border: none;
  border-radius: 20px;
  background: rgba(20, 20, 30, 0.72);
  color: rgba(255, 255, 255, 0.88);
  font-size: 12px;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  pointer-events: auto;
  backdrop-filter: blur(10px);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.35);
  transition: all 0.2s ease;
  letter-spacing: 0.3px;
}

.seg-toggle svg {
  width: 15px;
  height: 15px;
  flex-shrink: 0;
  transition: stroke 0.2s;
}

.seg-toggle:hover {
  background: rgba(40, 40, 55, 0.9);
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
}

.seg-toggle.active {
  background: rgba(76, 175, 80, 0.85);
  color: white;
  box-shadow: 0 2px 12px rgba(76, 175, 80, 0.45);
}

.seg-toggle.active:hover {
  background: rgba(56, 142, 60, 0.92);
}

.no-seg-badge {
  display: inline-block;
  padding: 5px 11px;
  border-radius: 20px;
  background: rgba(20, 20, 30, 0.55);
  color: rgba(255, 255, 255, 0.55);
  font-size: 11px;
  font-weight: 500;
  backdrop-filter: blur(8px);
  pointer-events: none;
}

.clickable {
  cursor: zoom-in;
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

/* ⭐ NUEVAS REGLAS PARA ALINEAR ÍCONO Y TEXTO ⭐ */
.structure-cell {
  display: flex;
  align-items: center; /* Alinea verticalmente al centro */
  gap: 12px; /* Espacio entre el icono y la palabra */
}

.table-icon {
  width: 18px; /* Tamaño perfecto para texto normal */
  height: 18px;
  flex-shrink: 0;
}

.count {
  font-weight: 700;
  font-size: 15px; /* Un poco más sutil */
  text-align: right; /* Alineado a la derecha como en tu imagen */
  color: #2c3e50;
  vertical-align: middle; /* Asegura que el número no flote arriba o abajo */
}

.count.critical {
  color: #ef5350; /* Rojo para destacar micronúcleos */
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

/* OVERLAY EDICIÓN (Nuevo diseño oscuro y flechas integradas) */
.image-editor-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.85); /* Fondo más oscuro para el "modo cine" */
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  animation: fadeIn 0.3s ease;
}

.editor-container {
  position: relative;
  background: transparent;
  border-radius: 0;
  padding: 0;
  width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 20px;
  box-shadow: none;
}

/* ⭐ ESTA ES LA CLASE QUE TE FALTABA ⭐ */
.editor-layout {
  display: flex;
  flex-direction: row; /* Fuerza a que estén en fila (lado a lado) */
  flex-wrap: nowrap; /* Prohíbe terminantemente que se bajen de línea */
  align-items: center;
  justify-content: center;
  gap: 40px;
  width: 100%;
  padding: 0 40px;
}

.editor-sidebar-right {
  border-left: 1px solid #2a2a2a;
  border-right: none;
}

/* --- PANEL LATERAL TIPO GLASSMORPHISM --- */
.editor-sidebar {
  width: 130px;
  min-width: 130px;
  max-width: 130px;
  box-sizing: border-box;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px 12px;
  background: rgba(30, 30, 35, 0.65);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
  z-index: 100;
}

.editor-sidebar-right {
  width: 220px;
  min-width: 220px;
  max-width: 220px;
  border-left: 1px solid rgba(255, 255, 255, 0.08);
}

.editor-image-wrapper {
  position: relative;
  /* ⭐ Restamos: 130px (izq) + 220px (der) + 80px (gaps) = 430px */
  max-width: calc(100vw - 430px);
  max-height: 85vh;
  width: 100%;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #1a1a1a;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.5);
}

.editor-image {
  max-width: 100%;
  max-height: 85vh;
  object-fit: contain;
  border-radius: 12px;
  background: #2c2c2c;
  user-select: none;
  -webkit-user-drag: none;
}

/* --- BOTONES (BASE PARA EL IZQUIERDO) --- */
.tool-option {
  display: flex;
  flex-direction: column; /* Icono arriba, texto abajo */
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 6px;
  width: 100%;
  box-sizing: border-box;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  background: rgba(20, 20, 25, 0.4);
  color: #a0a0b0;
  font-size: 11px;
  line-height: 1.2;
  text-align: center;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.tool-option span {
  display: block;
  width: 100%;
  white-space: normal;
  word-wrap: break-word;
}

.elegant-icon {
  width: 26px;
  height: 26px;
  transition: all 0.3s ease;
}

/* ⭐ EXCLUSIVO PARA LOS BOTONES DEL PANEL DERECHO ⭐ */
.editor-sidebar-right .tool-option {
  flex-direction: row; /* Icono a la izquierda, texto a la derecha */
  justify-content: flex-start; /* Alineado a la izquierda */
  padding: 12px 16px;
  gap: 12px;
  font-size: 13px; /* Letra un poquito más grande */
  text-align: left;
}

.editor-sidebar-right .elegant-icon {
  width: 20px; /* Icono más pequeño para formato fila */
  height: 20px;
  flex-shrink: 0;
}

.tool-option:hover {
  background: rgba(50, 50, 60, 0.8);
  transform: translateY(-2px);
  color: white;
}

/* Nuevos estilos para las flechas integradas */
.nav-arrow {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 52px;
  height: 52px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.35);
  color: #ffffff;
  font-size: 36px;
  cursor: pointer;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  backdrop-filter: blur(6px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
}

.nav-arrow:hover {
  background: rgba(255, 255, 255, 0.7);
  color: black;
  transform: translateY(-50%) scale(1.1);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.5);
  border-color: white;
}

.nav-arrow.left {
  left: 16px;
}
.nav-arrow.right {
  right: 16px;
}
.nav-arrow:disabled {
  opacity: 0;
  pointer-events: none;
}

/* Botón de cerrar rediseñado */
.close-btn {
  position: absolute;
  top: 20px;
  right: 40px;
  border: none;
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.8);
  width: 44px;
  height: 44px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 20px;
  z-index: 110;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: rgba(239, 83, 80, 0.8);
  color: white;
  transform: rotate(90deg);
}

/* --- BOTONES INACTIVOS --- */
.tool-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 14px 8px;
  width: 100%;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  background: rgba(20, 20, 25, 0.4);
  color: #a0a0b0;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.tool-option:hover {
  background: rgba(50, 50, 60, 0.8);
  transform: translateY(-2px);
  color: white;
}

.elegant-icon {
  width: 26px;
  height: 26px;
  transition: all 0.3s ease;
}

/* --- ESTADOS ACTIVOS (ILUMINACIÓN ESPECÍFICA) --- */
.tool-option.active.membrana-active {
  background: linear-gradient(135deg, rgba(46, 125, 50, 0.8), rgba(27, 94, 32, 0.9));
  border-color: #4caf50;
  color: white;
  box-shadow: 0 0 16px rgba(76, 175, 80, 0.4);
}
.tool-option.active.membrana-active .elegant-icon {
  stroke: white;
}
.tool-option.active.membrana-active .elegant-icon circle {
  stroke: white;
}

.tool-option.active.nucleo-active {
  background: linear-gradient(135deg, rgba(21, 101, 192, 0.8), rgba(13, 71, 161, 0.9));
  border-color: #1e88e5;
  color: white;
  box-shadow: 0 0 16px rgba(30, 136, 229, 0.4);
}
.tool-option.active.nucleo-active .elegant-icon {
  stroke: white;
}
.tool-option.active.nucleo-active .elegant-icon circle[fill] {
  fill: white;
}

.tool-option.active.micronucleo-active {
  background: linear-gradient(135deg, rgba(106, 27, 154, 0.8), rgba(74, 20, 140, 0.9));
  border-color: #ab47bc;
  color: white;
  box-shadow: 0 0 16px rgba(171, 71, 188, 0.4);
}
.tool-option.active.micronucleo-active .elegant-icon {
  stroke: white;
}
.tool-option.active.micronucleo-active .elegant-icon circle[fill] {
  fill: white;
}

.tool-option.active.borrar-active {
  background: linear-gradient(135deg, rgba(97, 97, 97, 0.8), rgba(66, 66, 66, 0.9));
  border-color: #9e9e9e;
  color: white;
  box-shadow: 0 0 16px rgba(158, 158, 158, 0.4);
}
.tool-option.active.borrar-active .elegant-icon {
  stroke: white;
}

.tool-option.active.editar-active {
  background: linear-gradient(135deg, rgba(123, 97, 255, 0.9), rgba(94, 53, 177, 0.9));
  border-color: #8c9eff;
  color: white;
  box-shadow: 0 0 20px rgba(123, 97, 255, 0.6);
}
.tool-option.active.editar-active .elegant-icon {
  stroke: white;
}

/* ANIMACIÓN */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* Ajustes responsivos */
@media (max-width: 768px) {
  .editor-image-wrapper {
    max-width: 95vw;
    max-height: 70vh;
  }
  .nav-arrow {
    width: 40px;
    height: 40px;
    font-size: 28px;
  }
  .nav-arrow.left {
    left: 8px;
  }
  .nav-arrow.right {
    right: 8px;
  }
  .close-btn {
    top: -45px;
    right: 10px;
  }
}

@media (max-width: 1200px) {
  /* Galería más delgada */
  .gallery-column {
    width: 120px; /* antes 230px */
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

/* ── EDITOR: MASCARA OVERLAY ── */
.editor-mask-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: contain;
  pointer-events: none;
  z-index: 5;
  opacity: 0.85;
  border-radius: 12px;
  transform-origin: center center;
}

/* ── EDITOR: SEPARADORES DE SECCION ── */
.editor-section-label {
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.35);
  padding: 0 4px;
  margin-top: 4px;
}

/* ── EDITOR: PANEL DE INFO ── */
.editor-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 8px;
  background: rgba(0, 0, 0, 0.25);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.editor-info-row {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.75);
  white-space: nowrap;
}

.editor-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
  opacity: 0.9;
}

.editor-no-data {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.3);
  text-align: center;
  padding: 4px 0;
}

/* ── EDITOR: INDICADOR DE ZOOM ── */
.zoom-indicator {
  position: absolute;
  bottom: 14px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.55);
  color: rgba(255, 255, 255, 0.8);
  font-size: 11px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 20px;
  backdrop-filter: blur(8px);
  pointer-events: none;
  z-index: 20;
}

/* ── EDITOR: ESTADO ACTIVO OVERLAY ── */
.tool-option.active.overlay-active {
  background: rgba(144, 202, 249, 0.2);
  border-color: rgba(144, 202, 249, 0.5);
  box-shadow: 0 0 10px rgba(144, 202, 249, 0.25);
}

/* ── EDICION ── */
/* ── Edicion Inactivo ── */
.tool-option:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* Color especial (Teal/Verde Azulado) para el Switch Maestro de Edición */
.tool-option.active.modo-edicion-active {
  /* Un degradado diferente para que se note que es un control principal */
  background: linear-gradient(135deg, rgba(0, 188, 212, 0.8), rgba(0, 151, 167, 0.9));
  border-color: #00bcd4;
  color: white;
  box-shadow: 0 0 20px rgba(0, 188, 212, 0.5);
}
/* Asegura que el candado se pinte de blanco al activarse */
.tool-option.active.modo-edicion-active .elegant-icon {
  stroke: white;
}

</style>
