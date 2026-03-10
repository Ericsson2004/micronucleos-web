<template>
  <div class="caract-portal">
    <!-- ══════════════ OVERLAY: SIN CASO SELECCIONADO ══════════════ -->
    <transition name="overlay-fade">
      <div v-if="!caseId" class="no-case-overlay">
        <div class="no-case-card">
          <div class="no-case-icon">
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="1.5"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
              <path d="M7 11V7a5 5 0 0 1 10 0v4" />
            </svg>
          </div>
          <h2 class="no-case-title">Selecciona un caso</h2>
          <p class="no-case-desc">
            Para ver la caracterización, primero selecciona un paciente y su caso desde
            <strong>Segmentación</strong>.
          </p>
          <div class="no-case-steps">
            <div class="step">
              <span class="step-num">1</span><span>Ve a <strong>Segmentación</strong></span>
            </div>
            <div class="step-arrow">→</div>
            <div class="step">
              <span class="step-num">2</span><span>Elige un <strong>paciente</strong></span>
            </div>
            <div class="step-arrow">→</div>
            <div class="step">
              <span class="step-num">3</span><span>Selecciona un <strong>caso</strong></span>
            </div>
          </div>
        </div>
      </div>
    </transition>

    <!-- ══════════════ KPI CARDS ══════════════ -->
    <div class="kpi-row">
      <div
        class="kpi-card"
        v-for="(kpi, i) in kpiCards"
        :key="i"
        :style="{ animationDelay: i * 0.08 + 's' }"
        :class="kpi.variant"
      >
        <div class="kpi-icon-wrap">
          <svg
            class="kpi-svg"
            viewBox="0 0 24 24"
            fill="none"
            :stroke="kpi.color"
            stroke-width="1.5"
            stroke-linecap="round"
            stroke-linejoin="round"
            v-html="kpi.svgPath"
          ></svg>
        </div>
        <div class="kpi-body">
          <div class="kpi-value">
            <span class="kpi-number animated-number" :data-target="kpi.value">{{
              kpi.displayValue
            }}</span>
            <span class="kpi-unit">{{ kpi.unit }}</span>
          </div>
          <div class="kpi-label">{{ kpi.label }}</div>
        </div>
        <div class="kpi-bar">
          <div class="kpi-bar-fill" :style="{ width: kpi.pct + '%', background: kpi.color }"></div>
        </div>
      </div>

      <!-- 6to card: Acciones -->
      <div class="kpi-card kpi-actions" :style="{ animationDelay: '0.4s' }">
        <div class="kpi-actions-label">Exportar</div>
        <button class="action-kpi-btn csv-btn">
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="7 10 12 15 17 10" />
            <line x1="12" y1="15" x2="12" y2="3" />
          </svg>
          Exportar CSV
        </button>
        <div class="kpi-actions-label">Reportes</div>
        <button class="action-kpi-btn pdf-btn">
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            <polyline points="14 2 14 8 20 8" />
            <line x1="9" y1="13" x2="15" y2="13" />
            <line x1="9" y1="17" x2="15" y2="17" />
          </svg>
          Generar PDF
        </button>
        <div class="kpi-bar" style="margin-top: auto">
          <div
            class="kpi-bar-fill"
            style="width: 100%; background: linear-gradient(90deg, #667eea, #764ba2)"
          ></div>
        </div>
      </div>
    </div>

    <!-- ══════════════ MAIN GRID ══════════════ -->
    <div class="main-grid">
      <!-- LEFT: Visor de imagen -->
      <section class="card viewer-card">
        <!-- Info paciente integrada en el visor -->
        <div class="viewer-info-bar">
          <div class="viewer-info-left">
            <span class="viewer-section-tag">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                <circle cx="12" cy="12" r="3" />
              </svg>
              Visualización
            </span>
            <div class="viewer-patient-chips">
              <span v-if="patientId" class="vchip vchip-patient">
                <svg
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                  <circle cx="12" cy="7" r="4" />
                </svg>
                Paciente {{ patientId }}
              </span>
              <span v-if="caseId" class="vchip vchip-case">
                <svg
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <path
                    d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"
                  />
                  <rect x="8" y="2" width="8" height="4" rx="1" />
                </svg>
                Caso {{ caseId }}
              </span>
              <span v-if="!patientId" class="vchip vchip-empty">Sin selección</span>
            </div>
          </div>
          <div class="nav-controls">
            <button class="nav-btn" @click="prevImage" :disabled="currentImageIndex === 0">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2.5"
                stroke-linecap="round"
              >
                <polyline points="15 18 9 12 15 6" />
              </svg>
            </button>
            <span class="nav-count">{{ currentImageIndex + 1 }} / {{ imageList.length }}</span>
            <button
              class="nav-btn"
              @click="nextImage"
              :disabled="currentImageIndex === imageList.length - 1"
            >
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2.5"
                stroke-linecap="round"
              >
                <polyline points="9 18 15 12 9 6" />
              </svg>
            </button>
          </div>
        </div>

        <div class="image-frame">
          <div class="image-layers">
            <img
              v-if="currentImage.src"
              :src="currentImage.src"
              :alt="currentImage.title"
              class="main-image base-layer"
              :key="'base-' + currentImage.id"
            />
            <img
              v-if="currentImage.maskSrc"
              :src="currentImage.maskSrc"
              class="main-image mask-layer"
              :key="'mask-' + currentImage.id"
            />

            <div v-if="!currentImage.src" style="color: #9ca3af; font-size: 14px; font-weight: 500">
              No hay imágenes para este caso
            </div>
          </div>

          <div class="image-legend">
            <div class="legend-item">
              <span class="legend-dot" style="background: #1e88e5"></span>
              Membrana
            </div>
            <div class="legend-item">
              <span class="legend-dot" style="background: #4caf50"></span>
              Núcleo
            </div>
            <div class="legend-item">
              <span class="legend-dot" style="background: #ef4444"></span>
              Micronúcleo
            </div>
            <div class="legend-item">
              <span class="legend-dot" style="background: #f59e0b"></span>
              Alerta
            </div>
          </div>
        </div>

        <!-- Thumbnails -->
        <div class="thumbnails-row">
          <button
            v-for="(img, idx) in imageList"
            :key="idx"
            class="thumb"
            :class="{ active: currentImage.id === img.id }"
            @click="selectImage(img)"
          >
            <img :src="img.src" :alt="img.title" />
            <div class="thumb-overlay">
              <span class="thumb-id">#{{ img.id }}</span>
            </div>
          </button>
        </div>
      </section>

      <!-- RIGHT: Tabla + mini-stats -->
      <section class="right-column">
        <!-- Mini distribución visual -->
        <div class="card dist-card">
          <div class="card-header">
            <h3 class="card-title">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="#667eea"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                style="width: 16px; height: 16px; flex-shrink: 0"
              >
                <rect x="3" y="3" width="18" height="18" rx="2" />
                <path d="M8 17V13M12 17V9M16 17V12" />
              </svg>
              Distribución de Estructuras — {{ currentImage.title }}
            </h3>
          </div>
          <div class="dist-bars">
            <div class="dist-row" v-for="(bar, i) in distributionBars" :key="i">
              <div class="dist-label-group">
                <svg
                  class="dist-icon"
                  viewBox="0 0 24 24"
                  fill="none"
                  :stroke="bar.color"
                  stroke-width="1.5"
                  v-html="bar.svgPath"
                ></svg>
                <span class="dist-label">{{ bar.label }}</span>
              </div>
              <div class="dist-track">
                <div
                  class="dist-fill"
                  :style="{ width: bar.pct + '%', background: bar.color }"
                  :class="'fill-' + bar.key"
                ></div>
              </div>
              <span class="dist-count" :style="{ color: bar.color }">{{ bar.count }}</span>
            </div>
          </div>
        </div>

        <!-- Tabla de resultados -->
        <div class="card table-card">
          <div class="card-header">
            <h3 class="card-title">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="#667eea"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                style="width: 16px; height: 16px; flex-shrink: 0"
              >
                <path d="M3 3h18v18H3zM3 9h18M3 15h18M9 3v18M15 3v18" />
              </svg>
              Resultados por Membrana
            </h3>
            <div class="search-mini">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="#999"
                stroke-width="2"
                style="width: 14px; height: 14px; flex-shrink: 0"
              >
                <circle cx="11" cy="11" r="8" />
                <line x1="21" y1="21" x2="16.65" y2="16.65" />
              </svg>
              <input
                type="text"
                v-model="searchQuery"
                placeholder="Filtrar..."
                class="search-mini-input"
              />
            </div>
          </div>

          <div class="table-wrapper">
            <table class="data-table">
              <thead>
                <tr>
                  <th @click="sortBy('id')" class="sortable">
                    ID
                    <span class="sort-icon" :class="{ active: sortKey === 'id' }">{{ sortKey === "id" ? (sortDir === "asc" ? "↑" : "↓") : "↕" }}</span>
                  </th>
                  <th @click="sortBy('areaNucleo')" class="sortable">
                    Área Núcleo
                    <span class="sort-icon" :class="{ active: sortKey === 'areaNucleo' }">{{ sortKey === "areaNucleo" ? (sortDir === "asc" ? "↑" : "↓") : "↕" }}</span>
                  </th>
                  <th @click="sortBy('areaMN')" class="sortable">
                    Área MN
                    <span class="sort-icon" :class="{ active: sortKey === 'areaMN' }">{{ sortKey === "areaMN" ? (sortDir === "asc" ? "↑" : "↓") : "↕" }}</span>
                  </th>
                  <th @click="sortBy('intNucleo')" class="sortable">
                    Int. Núcleo
                    <span class="sort-icon" :class="{ active: sortKey === 'intNucleo' }">{{ sortKey === "intNucleo" ? (sortDir === "asc" ? "↑" : "↓") : "↕" }}</span>
                  </th>
                  <th @click="sortBy('intMN')" class="sortable">
                    Int. MN
                    <span class="sort-icon" :class="{ active: sortKey === 'intMN' }">{{ sortKey === "intMN" ? (sortDir === "asc" ? "↑" : "↓") : "↕" }}</span>
                  </th>
                  <th @click="sortBy('redondezNucleo')" class="sortable">
                    Redondez N.
                    <span class="sort-icon" :class="{ active: sortKey === 'redondezNucleo' }">{{ sortKey === "redondezNucleo" ? (sortDir === "asc" ? "↑" : "↓") : "↕" }}</span>
                  </th>
                  <th @click="sortBy('redondezMN')" class="sortable">
                    Redondez MN
                    <span class="sort-icon" :class="{ active: sortKey === 'redondezMN' }">{{ sortKey === "redondezMN" ? (sortDir === "asc" ? "↑" : "↓") : "↕" }}</span>
                  </th>
                  <th @click="sortBy('distancia')" class="sortable" style="color: #667eea;">
                    Distancia
                    <span class="sort-icon" :class="{ active: sortKey === 'distancia' }">{{ sortKey === "distancia" ? (sortDir === "asc" ? "↑" : "↓") : "↕" }}</span>
                  </th>
                  <th @click="sortBy('fraccionArea')" class="sortable" style="color: #667eea;">
                    Fra. Área
                    <span class="sort-icon" :class="{ active: sortKey === 'fraccionArea' }">{{ sortKey === "fraccionArea" ? (sortDir === "asc" ? "↑" : "↓") : "↕" }}</span>
                  </th>
                  <th @click="sortBy('fraccionInt')" class="sortable" style="color: #667eea;">
                    Fra. Int.
                    <span class="sort-icon" :class="{ active: sortKey === 'fraccionInt' }">{{ sortKey === "fraccionInt" ? (sortDir === "asc" ? "↑" : "↓") : "↕" }}</span>
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(row, idx) in filteredSortedData"
                  :key="row.id"
                  class="data-row"
                  :class="{ 'row-alert': row.areaMN > 0, 'row-selected': selectedRow === row.id }"
                  @click="selectedRow = selectedRow === row.id ? null : row.id"
                  :style="{ animationDelay: idx * 0.04 + 's' }"
                >
                  <td class="cell-id">#{{ row.id_membrana || row.id }}</td>

                  <td>{{ row.areaNucleo ? row.areaNucleo.toFixed(1) : '-' }}</td>

                  <td>
                    <span v-if="row.areaMN" class="mn-count-badge critical" style="background: transparent; box-shadow: none; color: #ef4444;">
                      {{ row.areaMN.toFixed(1) }}
                    </span>
                    <span v-else>-</span>
                  </td>

                  <td>{{ row.intNucleo ? row.intNucleo.toFixed(2) : '-' }}</td>

                  <td>{{ row.intMN ? row.intMN.toFixed(2) : '-' }}</td>

                  <td>
                    <div v-if="row.redondezNucleo" class="circularity-badge" :class="circularityClass(row.redondezNucleo)">
                      {{ row.redondezNucleo.toFixed(3) }}
                    </div>
                    <span v-else>-</span>
                  </td>

                  <td>
                    <div v-if="row.redondezMN" class="circularity-badge" :class="circularityClass(row.redondezMN)">
                      {{ row.redondezMN.toFixed(3) }}
                    </div>
                    <span v-else>-</span>
                  </td>

                  <td style="font-weight: 600; color: #4b5563;">{{ row.distancia ? row.distancia.toFixed(2) : '-' }}</td>

                  <td style="font-weight: 600; color: #667eea;">{{ row.fraccionArea ? row.fraccionArea.toFixed(3) : '-' }}</td>

                  <td style="font-weight: 600; color: #667eea;">{{ row.fraccionInt ? row.fraccionInt.toFixed(3) : '-' }}</td>
                </tr>
                <tr v-if="filteredSortedData.length === 0">
                  <td colspan="10" class="empty-state">
                    <div class="empty-icon">🔬</div>
                    <p>Sin resultados para la búsqueda</p>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Table footer with actions -->
          <div class="table-footer">
            <span class="row-count"
              >{{ filteredSortedData.length }} membranas · {{ alertCount }} con alertas</span
            >
            <div class="footer-actions">
              <button
                class="btn-action btn-back"
                @click="$emit('go-segmentacion')"
                style="padding: 8px 14px; font-size: 12px"
              >
                <svg
                  class="btn-svg"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <polyline points="15 18 9 12 15 6" />
                </svg>
                Segmentación
              </button>
              <button
                class="btn-action primary btn-caracterizar"
                :class="{ loading: isCharacterizing }"
                :disabled="isCharacterizing"
                @click="caracterizar"
                style="padding: 8px 16px; font-size: 12px"
              >
                <svg
                  v-if="isCharacterizing"
                  class="btn-svg spinner"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2.5"
                >
                  <path
                    d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"
                  />
                </svg>
                <svg
                  v-else
                  class="btn-svg"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <circle cx="12" cy="12" r="3" />
                  <path
                    d="M12 1v4M12 19v4M4.22 4.22l2.83 2.83M16.95 16.95l2.83 2.83M1 12h4M19 12h4M4.22 19.78l2.83-2.83M16.95 7.05l2.83-2.83"
                  />
                </svg>
                {{ isCharacterizing ? "Procesando…" : "Caracterizar" }}
              </button>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import axios from "@/axios.js";

const props = defineProps({
  patientId: { type: [Number, String], default: null },
  caseId: { type: [Number, String], default: null },
  refreshKey: { type: Number, default: 0 },
});

console.log("Paciente recibido:", props.patientId);
console.log("Caso recibido:", props.caseId);

defineEmits(["go-segmentacion"]);

// ── Cargar Imagenes ──────────────────────────────

const loadingData = ref(false);

async function obtenerMascaraSegura(urlParcial) {
  if (!urlParcial) return null;
  try {
    // Apuntamos directo a Django para evitar que Axios duplique el /api/
    const urlCompleta = urlParcial.startsWith('http') ? urlParcial : `http://127.0.0.1:8000${urlParcial}`;

    // Al pedirlo con axios, se envía tu token JWT automáticamente
    const res = await axios.get(urlCompleta, { responseType: "blob" });
    return URL.createObjectURL(res.data);
  } catch (e) {
    console.error("Error al descargar máscara:", e);
    return null;
  }
}

async function cargarDatos() {
  if (!props.caseId) return;
  limpiarBlobUrls();

  loadingData.value = true;
  console.log(`Intentando pedir datos del caso: ${props.caseId}`);

  try {
    const response = await axios.get(`/api/casos/${props.caseId}/caracterizacion/`);
    const data = response.data;
    console.log("¡Datos recibidos con éxito!", data);

    // 1. Mapeamos usando directamente la IP de Django para las imágenes base
    imageList.value = data.imagenes.map((img) => ({
      id: img.id,
      title: img.title,
      src: img.src.startsWith('http') ? img.src : `http://127.0.0.1:8000${img.src}`,
      maskSrc: null,
      _rawMaskUrl: img.mask_src
    }));

    // Llenamos la tabla y las gráficas INMEDIATAMENTE
    tableData.value = data.membranas || [];
    currentImageIndex.value = 0;

    // 2. Descargamos las máscaras sin bloquear la pantalla y le avisamos a Vue
    imageList.value.forEach((img, index) => {
      if (img._rawMaskUrl) {
        obtenerMascaraSegura(img._rawMaskUrl).then((blobUrl) => {
          if (blobUrl) {
            // Actualizamos la propiedad reactiva para que la imagen aparezca sola
            imageList.value[index].maskSrc = blobUrl;
          }
        });
      }
    });

  } catch (error) {
    console.error("🔥 Error cargando caracterización:", error);
  } finally {
    loadingData.value = false;
  }
}

function limpiarBlobUrls() {
  imageList.value.forEach(img => {
    if (img.maskSrc && img.maskSrc.startsWith('blob:')) {
      URL.revokeObjectURL(img.maskSrc);
    }
  });
}

onMounted(() => {
  if (props.caseId) {
    cargarDatos();
  }
});

watch(
  () => props.caseId,
  () => {
    cargarDatos();
  },
);

watch(
  () => props.refreshKey,
  () => {
    if (props.caseId) {
      console.log("🔄 Actualización detectada por refreshKey, recargando caracterización...");
      cargarDatos();
    }
  }
);

// ── Caracterización ──────────────────────────────
const isCharacterizing = ref(false);

async function caracterizar() {
  if (isCharacterizing.value) return;
  isCharacterizing.value = true;
  try {
    await new Promise((r) => setTimeout(r, 1500));
  } finally {
    isCharacterizing.value = false;
  }
}

// ── Search & Sort ───────────────────────────────
const searchQuery = ref("");
const sortKey = ref("id_membrana"); // Actualizado para coincidir con backend
const sortDir = ref("asc");
const selectedRow = ref(null);

function sortBy(key) {
  if (sortKey.value === key) {
    sortDir.value = sortDir.value === "asc" ? "desc" : "asc";
  } else {
    sortKey.value = key;
    sortDir.value = "asc";
  }
}

// ── Image viewer ────────────────────────────────
const imageList = ref([]);

const currentImageIndex = ref(0);
const currentImage = computed(() => {
  return (
    imageList.value[currentImageIndex.value] || {
      id: 0,
      title: "Sin imagen",
      src: "",
    }
  );
});

function prevImage() {
  if (currentImageIndex.value > 0) currentImageIndex.value--;
}
function nextImage() {
  if (currentImageIndex.value < imageList.value.length - 1) currentImageIndex.value++;
}
function selectImage(img) {
  currentImageIndex.value = imageList.value.findIndex((i) => i.id === img.id);
}

// ── Table data ──────────────────────────────────
// Inicia vacío para evitar que sume los datos quemados
const tableData = ref([]);

const maxSize = computed(() => {
  if (tableData.value.length === 0) return 100;
  return Math.max(...tableData.value.map((r) => r.size || 0));
});

const filteredSortedData = computed(() => {
  let data = tableData.value;
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase();
    data = data.filter((r) => String(r.id_membrana).includes(q) || String(r.mn_count).includes(q));
  }
  return [...data].sort((a, b) => {
    const va = a[sortKey.value] || 0,
      vb = b[sortKey.value] || 0;
    return sortDir.value === "asc" ? va - vb : vb - va;
  });
});

const alertCount = computed(() => tableData.value.filter((r) => (r.mn_count || 0) > 2).length);

// ── KPI cards ──────────────────────────────────
const kpiCards = computed(() => {
  const total = tableData.value.length;
  // Calculamos todo en base a las variables reales del backend (snake_case)
  const totalMN = tableData.value.reduce((s, r) => s + (r.mn_count || 0), 0);
  const avgCirc = total
    ? (tableData.value.reduce((s, r) => s + (r.circularity || 0), 0) / total).toFixed(2)
    : "0.00";
  const avgSize = total
    ? (tableData.value.reduce((s, r) => s + (r.size || 0), 0) / total).toFixed(1)
    : "0.0";

  // Frecuencia = Micronúcleos totales / Membranas totales * 100 (Según tu instrucción)
  const mnFreq = total ? ((totalMN / total) * 100).toFixed(1) : "0.0";

  return [
    {
      label: "Membranas analizadas",
      value: total,
      displayValue: total,
      unit: "",
      color: "#1e88e5",
      variant: "kpi-blue",
      pct: 100,
      svgPath:
        '<circle cx="12" cy="12" r="7" stroke-dasharray="3 3"/><circle cx="12" cy="12" r="4"/>',
    },
    {
      label: "Total micronúcleos",
      value: totalMN,
      displayValue: totalMN,
      unit: "µN",
      color: "#ef4444",
      variant: "kpi-red",
      pct: Math.min(totalMN * 5, 100),
      svgPath:
        '<circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.5" fill="#ef4444" stroke="none"/>',
    },
    {
      label: "Frecuencia µN",
      value: parseFloat(mnFreq),
      displayValue: mnFreq,
      unit: "%",
      color: "#f59e0b",
      variant: "kpi-yellow",
      pct: parseFloat(mnFreq),
      svgPath: '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>',
    },
    {
      label: "Circularidad media",
      value: parseFloat(avgCirc),
      displayValue: avgCirc,
      unit: "",
      color: "#4caf50",
      variant: "kpi-green",
      pct: parseFloat(avgCirc) * 100,
      svgPath: '<circle cx="12" cy="12" r="9"/><path d="M12 3a9 9 0 0 1 6.36 15.36"/>',
    },
    {
      label: "Tamaño medio",
      value: parseFloat(avgSize),
      displayValue: avgSize,
      unit: "µm³",
      color: "#667eea",
      variant: "kpi-indigo",
      pct: maxSize.value > 0 ? (parseFloat(avgSize) / maxSize.value) * 100 : 0,
      svgPath:
        '<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>',
    },
  ];
});

// ── Distribution bars ──────────────────────────
const distributionBars = computed(() => {
  // 1. Filtramos los datos de la tabla para que solo queden los de la imagen actual
  const currentImageId = currentImage.value.id;
  const datosImagenActual = tableData.value.filter(r => r.id_muestra === currentImageId);

  // 2. Calculamos los totales usando SOLO los datos filtrados
  const totalMembranas = datosImagenActual.length;
  const totalNucleos = totalMembranas; // Asumimos 1 núcleo por membrana para mantener la visualización
  const mnSum = datosImagenActual.reduce((s, r) => s + (r.mn_count || 0), 0);
  const alertas = datosImagenActual.filter((r) => (r.mn_count || 0) > 2).length;

  const mnPct = totalMembranas ? Math.min(Math.round((mnSum / (totalMembranas * 5)) * 100), 100) : 0;
  const pctAlertas = totalMembranas ? Math.round((alertas / totalMembranas) * 100) : 0;

  return [
    {
      key: "nucleos",
      label: "Núcleos",
      count: totalNucleos,
      color: "#4caf50",
      pct: totalNucleos > 0 ? 100 : 0,
      svgPath:
        '<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="3" fill="#4caf50" stroke="none"/>',
    },
    {
      key: "membranas",
      label: "Membranas",
      count: totalMembranas,
      color: "#1e88e5",
      pct: totalMembranas > 0 ? 100 : 0,
      svgPath:
        '<circle cx="12" cy="12" r="7" stroke-dasharray="3 3"/><circle cx="12" cy="12" r="3"/>',
    },
    {
      key: "micronucleos",
      label: "Micronúcleos",
      count: mnSum,
      color: "#ef4444",
      pct: mnPct,
      svgPath:
        '<circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.5" fill="#ef4444" stroke="none"/>',
    },
    {
      key: "alertas",
      label: "Células con alerta (µN > 2)",
      count: alertas,
      color: "#f59e0b",
      pct: pctAlertas,
      svgPath:
        '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>',
    },
  ];
});

// ── Helpers ────────────────────────────────────
function circularityClass(c) {
  if (c >= 0.9) return "circ-high";
  if (c >= 0.75) return "circ-mid";
  return "circ-low";
}

</script>

<style scoped>
/* ─────────────────────────────────────────────
   ROOT — ajuste a la altura disponible sin desbordar
───────────────────────────────────────────── */
.caract-portal {
  flex: 1;
  padding: 10px 14px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  overflow: hidden; /* NO scroll en el portal, la tabla tiene el suyo */
  background: #f8f9fa;
  height: calc(100vh - 60px); /* resta la TopBar */
  box-sizing: border-box;
}

/* ─────────────────────────────────────────────
   BUTTONS
───────────────────────────────────────────── */
.btn-action {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 7px 13px;
  border: 1.5px solid #e0e0e0;
  background: white;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  border-radius: 8px;
  color: #2c3e50;
  transition: all 0.2s ease;
}
.btn-action:hover {
  transform: translateY(-1px);
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
}
.btn-action.csv:hover {
  border-color: #43a047;
  background: #e8f5e9;
}
.btn-action.pdf:hover {
  border-color: #e53935;
  background: #ffebee;
}
.btn-action.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: transparent;
}
.btn-action.primary:hover {
  opacity: 0.9;
  box-shadow: 0 3px 12px rgba(102, 126, 234, 0.4);
}
.btn-svg {
  width: 13px;
  height: 13px;
  flex-shrink: 0;
}

/* Botón Atrás */
.btn-back {
  color: #6b7280;
  gap: 4px;
}
.btn-back:hover {
  border-color: #667eea;
  color: #667eea;
  background: #f0f4ff;
}
.btn-back svg {
  transition: transform 0.2s ease;
}
.btn-back:hover svg {
  transform: translateX(-2px);
}

/* Botón Caracterizar */
.btn-caracterizar:disabled {
  cursor: not-allowed;
  opacity: 0.85;
}
.btn-caracterizar.loading {
  background: linear-gradient(135deg, #7c8fea 0%, #8b5bb5 100%);
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
.spinner {
  animation: spin 0.75s linear infinite;
}

/* ─────────────────────────────────────────────
   NO-CASE OVERLAY
───────────────────────────────────────────── */
.caract-portal {
  position: relative;
}

.no-case-overlay {
  position: absolute;
  inset: 0;
  z-index: 50;
  backdrop-filter: blur(6px) brightness(0.97);
  -webkit-backdrop-filter: blur(6px) brightness(0.97);
  background: rgba(240, 242, 245, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
}
.no-case-card {
  background: white;
  border-radius: 20px;
  padding: 48px 56px;
  box-shadow:
    0 24px 60px rgba(0, 0, 0, 0.12),
    0 4px 16px rgba(102, 126, 234, 0.1);
  text-align: center;
  max-width: 440px;
  animation: cardPop 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}
@keyframes cardPop {
  from {
    opacity: 0;
    transform: scale(0.88) translateY(16px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}
.no-case-icon {
  width: 72px;
  height: 72px;
  background: linear-gradient(135deg, #eef2ff 0%, #e0e7ff 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  animation: lockWiggle 3s ease-in-out infinite;
}
.no-case-icon svg {
  width: 32px;
  height: 32px;
  stroke: #667eea;
}
@keyframes lockWiggle {
  0%,
  80%,
  100% {
    transform: rotate(0deg);
  }
  85% {
    transform: rotate(-8deg);
  }
  90% {
    transform: rotate(8deg);
  }
  95% {
    transform: rotate(-4deg);
  }
}
.no-case-title {
  font-size: 22px;
  font-weight: 700;
  margin: 0 0 10px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.no-case-desc {
  font-size: 14px;
  color: #6b7280;
  line-height: 1.6;
  margin: 0 0 28px;
}
.no-case-steps {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  flex-wrap: wrap;
}
.step {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #4b5563;
  background: #f8f9fa;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 6px 10px;
}
.step-num {
  width: 18px;
  height: 18px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border-radius: 50%;
  font-size: 10px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.step-arrow {
  color: #9ca3af;
  font-size: 14px;
}

.overlay-fade-enter-active {
  transition: opacity 0.25s ease;
}
.overlay-fade-leave-active {
  transition: opacity 0.3s ease;
}
.overlay-fade-enter-from,
.overlay-fade-leave-to {
  opacity: 0;
}

/* ─────────────────────────────────────────────
   KPI ROW — altura fija, no crece
───────────────────────────────────────────── */
.kpi-row {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 8px;
  flex-shrink: 0;
  height: 88px; /* altura fija compacta */
}

.kpi-card {
  background: white;
  border-radius: 10px;
  padding: 10px 12px 8px;
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.06);
  border: 1px solid #eeeeee;
  display: flex;
  flex-direction: column;
  gap: 3px;
  position: relative;
  overflow: hidden;
  animation: fadeInUp 0.4s ease both;
  transition:
    transform 0.2s,
    box-shadow 0.2s;
}
.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 16px rgba(0, 0, 0, 0.09);
}
.kpi-card::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  border-radius: 10px 10px 0 0;
}
.kpi-blue::before {
  background: #1e88e5;
}
.kpi-red::before {
  background: #ef4444;
}
.kpi-yellow::before {
  background: #f59e0b;
}
.kpi-green::before {
  background: #4caf50;
}
.kpi-indigo::before {
  background: #667eea;
}

/* 6to card: acciones */
.kpi-actions {
  justify-content: flex-start;
  gap: 4px;
  padding: 8px 10px;
}
.kpi-actions::before {
  background: linear-gradient(90deg, #667eea, #764ba2);
}
.kpi-actions-label {
  font-size: 8px;
  font-weight: 700;
  letter-spacing: 0.8px;
  text-transform: uppercase;
  color: #9ca3af;
  line-height: 1;
}
.action-kpi-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  width: 100%;
  padding: 4px 8px;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
  background: #f9fafb;
  cursor: pointer;
  font-size: 10px;
  font-weight: 600;
  color: #374151;
  transition: all 0.2s ease;
  text-align: left;
  line-height: 1.3;
}
.action-kpi-btn svg {
  width: 11px;
  height: 11px;
  flex-shrink: 0;
}
.action-kpi-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}
.csv-btn:hover {
  border-color: #43a047;
  background: #e8f5e9;
  color: #2e7d32;
}
.csv-btn:hover svg {
  stroke: #2e7d32;
}
.pdf-btn:hover {
  border-color: #e53935;
  background: #ffebee;
  color: #c62828;
}
.pdf-btn:hover svg {
  stroke: #c62828;
}

.kpi-icon-wrap {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  background: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.kpi-svg {
  width: 14px;
  height: 14px;
}
.kpi-body {
  flex: 1;
  min-height: 0;
}
.kpi-value {
  display: flex;
  align-items: baseline;
  gap: 3px;
}
.kpi-number {
  font-size: 18px;
  font-weight: 700;
  color: #1a202c;
  line-height: 1;
}
.kpi-unit {
  font-size: 10px;
  font-weight: 600;
  color: #9ca3af;
  text-transform: uppercase;
}
.kpi-label {
  font-size: 10px;
  color: #6b7280;
  margin-top: 1px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.kpi-bar {
  height: 3px;
  background: #f0f0f0;
  border-radius: 3px;
  overflow: hidden;
  margin-top: auto;
}
.kpi-bar-fill {
  height: 100%;
  border-radius: 3px;
  animation: growWidth 0.8s ease both;
  animation-delay: 0.3s;
}

/* ─────────────────────────────────────────────
   MAIN GRID — ocupa el espacio restante
───────────────────────────────────────────── */
.main-grid {
  display: grid;
  grid-template-columns: 1fr 1.6fr;
  gap: 10px;
  flex: 1;
  min-height: 0; /* crítico para que flex no explote */
}

/* ─────────────────────────────────────────────
   CARDS
───────────────────────────────────────────── */
.card {
  background: white;
  border-radius: 10px;
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.06);
  border: 1px solid #eeeeee;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0;
}
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 9px 12px 8px;
  border-bottom: 1px solid #f0f0f0;
  flex-shrink: 0;
}
.card-title {
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 0;
  font-size: 12px;
  font-weight: 600;
  color: #2c3e50;
}

/* ─────────────────────────────────────────────
   VIEWER CARD
───────────────────────────────────────────── */
/*.viewer-card {
}*/

/* Info bar compacta arriba del visor */
.viewer-info-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 7px 12px 6px;
  border-bottom: 1px solid #f0f0f0;
  flex-shrink: 0;
  gap: 8px;
}
.viewer-info-left {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  min-width: 0;
}
.viewer-section-tag {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.4px;
  color: #667eea;
  white-space: nowrap;
  flex-shrink: 0;
}
.viewer-section-tag svg {
  width: 11px;
  height: 11px;
  stroke: #667eea;
}
.viewer-patient-chips {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
}
.vchip {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  padding: 2px 7px;
  border-radius: 20px;
  font-size: 10px;
  font-weight: 500;
}
.vchip svg {
  width: 10px;
  height: 10px;
  flex-shrink: 0;
}
.vchip-patient {
  background: #f0f4f8;
  color: #4b5563;
}
.vchip-case {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
}
.vchip-case svg {
  stroke: white;
}
.vchip-empty {
  background: #f3f4f6;
  color: #9ca3af;
  font-style: italic;
}

/* Imagen */
.image-frame {
  position: relative;
  flex: 1;
  min-height: 0;
  background: #eef0f5;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  margin: 8px 12px 0;
  border-radius: 6px;
  border: 1px solid #e0e0e0;
}
.main-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  animation: fadeIn 0.3s ease;
  border-radius: 4px;
}
.image-legend {
  position: absolute;
  bottom: 8px;
  right: 8px;
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  padding: 5px 9px;
  display: flex;
  flex-direction: column;
  gap: 3px;
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.07);
  font-size: 10px;
  color: #4b5563;
}
.legend-item {
  display: flex;
  align-items: center;
  gap: 5px;
}
.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

/* Thumbnails */
.thumbnails-row {
  display: flex;
  gap: 7px;
  padding: 7px 12px;
  justify-content: flex-start;
  overflow-x: auto;
  flex-shrink: 0;
}
.thumb {
  position: relative;
  flex-shrink: 0;
  width: 64px;
  height: 44px;
  border: 2px solid transparent;
  border-radius: 6px;
  overflow: hidden;
  cursor: pointer;
  background: #f0f0f0;
  transition:
    border-color 0.2s,
    transform 0.15s,
    box-shadow 0.15s;
}
.thumb:hover {
  transform: scale(1.06);
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.1);
}
.thumb.active {
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
}
.thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.thumb-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1px 0;
}
.thumb-id {
  font-size: 9px;
  color: white;
  font-weight: 600;
}

/* Nav controls */
.nav-controls {
  display: flex;
  align-items: center;
  gap: 5px;
}
.nav-btn {
  width: 24px;
  height: 24px;
  border: 1px solid #e0e0e0;
  background: #f8f9fa;
  border-radius: 5px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}
.nav-btn svg {
  width: 12px;
  height: 12px;
}
.nav-btn:hover:not(:disabled) {
  background: #667eea;
  border-color: #667eea;
}
.nav-btn:hover:not(:disabled) svg {
  stroke: white;
}
.nav-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}
.nav-count {
  font-size: 11px;
  font-weight: 500;
  color: #6b7280;
  min-width: 32px;
  text-align: center;
}

/* ─────────────────────────────────────────────
   RIGHT COLUMN
───────────────────────────────────────────── */
.right-column {
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-height: 0;
}

/* Distribution bars */
.dist-card {
  flex-shrink: 0;
}
.dist-bars {
  padding: 8px 12px;
  display: flex;
  flex-direction: column;
  gap: 7px;
}
.dist-row {
  display: flex;
  align-items: center;
  gap: 8px;
}
.dist-label-group {
  display: flex;
  align-items: center;
  gap: 5px;
  width: 160px;
  flex-shrink: 0;
}
.dist-icon {
  width: 15px;
  height: 15px;
  flex-shrink: 0;
}
.dist-label {
  font-size: 11px;
  color: #4b5563;
  font-weight: 500;
  white-space: nowrap;
}
.dist-track {
  flex: 1;
  height: 7px;
  background: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
}
.dist-fill {
  height: 100%;
  border-radius: 4px;
  animation: growWidth 0.7s cubic-bezier(0.4, 0, 0.2, 1) both;
}
.dist-fill.fill-nucleos {
  animation-delay: 0.1s;
}
.dist-fill.fill-membranas {
  animation-delay: 0.2s;
}
.dist-fill.fill-micronucleos {
  animation-delay: 0.3s;
}
.dist-fill.fill-alertas {
  animation-delay: 0.4s;
}
.dist-count {
  font-size: 11px;
  font-weight: 700;
  min-width: 24px;
  text-align: right;
}

/* ─────────────────────────────────────────────
   TABLE CARD
───────────────────────────────────────────── */
.table-card {
  flex: 1;
  min-height: 0;
}

.search-mini {
  display: flex;
  align-items: center;
  gap: 5px;
  background: #f8f9fa;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  padding: 4px 9px;
}
.search-mini-input {
  border: none;
  background: transparent;
  outline: none;
  font-size: 11px;
  color: #2c3e50;
  width: 100px;
}
.search-mini-input::placeholder {
  color: #bbb;
}

.table-wrapper {
  flex: 1;
  overflow-y: auto;
  min-height: 0;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 11px;
  text-align: left;
}
.data-table thead {
  background: #f8f9fa;
  position: sticky;
  top: 0;
  z-index: 1;
  box-shadow: 0 1px 0 #e0e0e0;
}
.data-table th {
  padding: 7px 8px;
  font-weight: 600;
  font-size: 10px;
  color: #6b7280;
  white-space: nowrap;
  border-bottom: 1px solid #e0e0e0;
}
.data-table th.sortable {
  cursor: pointer;
  user-select: none;
}
.data-table th.sortable:hover {
  color: #667eea;
}
.sort-icon {
  font-size: 9px;
  color: #ccc;
  margin-left: 2px;
}
.sort-icon.active {
  color: #667eea;
}
.data-table td {
  padding: 6px 8px;
  border-bottom: 1px solid #f0f0f0;
  color: #374151;
}

.data-row {
  cursor: pointer;
  animation: fadeInUp 0.3s ease both;
  transition: background 0.12s;
}
.data-row:hover {
  background: #f5f7ff;
}
.data-row.row-selected {
  background: #eef2ff;
}
.data-row.row-alert td:first-child {
  border-left: 3px solid #f59e0b;
}
.data-row.row-alert {
  background: #fffbeb;
}

.cell-id {
  font-weight: 600;
  color: #6b7280;
  font-size: 10px;
}

.cell-bar-wrap {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.mini-bar {
  height: 2px;
  background: #f0f0f0;
  border-radius: 2px;
  width: 50px;
}
.mini-bar-fill {
  height: 100%;
  border-radius: 2px;
}

.circularity-badge {
  display: inline-block;
  padding: 1px 6px;
  border-radius: 20px;
  font-size: 10px;
  font-weight: 600;
}
.circ-high {
  background: #e8f5e9;
  color: #2e7d32;
}
.circ-mid {
  background: #fff8e1;
  color: #f57f17;
}
.circ-low {
  background: #fce4ec;
  color: #c62828;
}

.mn-count-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  font-size: 10px;
  font-weight: 700;
  background: #f0f4f8;
  color: #4b5563;
  transition: all 0.2s;
}
.mn-count-badge.critical {
  background: #fef3c7;
  color: #d97706;
  box-shadow: 0 0 0 2px rgba(245, 158, 11, 0.3);
  animation: pulseBadge 2s ease-in-out infinite;
}

.intensity-wrap {
  display: flex;
  align-items: center;
  gap: 5px;
}
.intensity-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}

.empty-state {
  text-align: center;
  padding: 30px 0;
  color: #9ca3af;
}
.empty-icon {
  font-size: 28px;
  margin-bottom: 6px;
}
.empty-state p {
  margin: 0;
  font-size: 12px;
}

.table-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 7px 12px;
  border-top: 1px solid #f0f0f0;
  flex-shrink: 0;
  background: #fafafa;
}
.row-count {
  font-size: 10px;
  color: #9ca3af;
}
.footer-actions {
  display: flex;
  gap: 6px;
}

/* ─────────────────────────────────────────────
   RESPONSIVE — iPad mini (768px) y abajo
───────────────────────────────────────────── */
@media (max-width: 900px) {
  .kpi-row {
    grid-template-columns: repeat(3, 1fr);
    height: auto;
  }
  .main-grid {
    grid-template-columns: 1fr;
    overflow-y: auto;
  }
  .caract-portal {
    overflow-y: auto;
    height: auto;
    min-height: calc(100vh - 60px);
  }
  .dist-label-group {
    width: 130px;
  }
}

@media (max-width: 600px) {
  .kpi-row {
    grid-template-columns: repeat(2, 1fr);
  }
  .caract-portal {
    padding: 8px;
  }
}

/* ─────────────────────────────────────────────
   ANIMATIONS
───────────────────────────────────────────── */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
@keyframes growWidth {
  from {
    width: 0 !important;
  }
}
@keyframes pulseBadge {
  0%,
  100% {
    box-shadow: 0 0 0 2px rgba(245, 158, 11, 0.3);
  }
  50% {
    box-shadow: 0 0 0 5px rgba(245, 158, 11, 0.1);
  }
}

/* ─────────────────────────────────────────────
   SCROLLBAR
───────────────────────────────────────────── */
.table-wrapper::-webkit-scrollbar,
.caract-portal::-webkit-scrollbar,
.main-grid::-webkit-scrollbar {
  width: 5px;
}
.table-wrapper::-webkit-scrollbar-track,
.caract-portal::-webkit-scrollbar-track,
.main-grid::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 10px;
}
.table-wrapper::-webkit-scrollbar-thumb,
.caract-portal::-webkit-scrollbar-thumb,
.main-grid::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
}

/* ─────────────────────────────────────────────
   CAPAS DE IMAGEN PARA MÁSCARAS
───────────────────────────────────────────── */
.image-layers {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.base-layer {
  position: absolute;
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.mask-layer {
  position: absolute;
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  z-index: 10;
  pointer-events: none;
}
</style>
