<template>
  <nav class="topbar">
    <!-- Botón hamburguesa (móvil) -->
    <button class="menu-btn" @click="$emit('toggle-sidebar')">
      <svg
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <line x1="3" y1="12" x2="21" y2="12" />
        <line x1="3" y1="6" x2="21" y2="6" />
        <line x1="3" y1="18" x2="21" y2="18" />
      </svg>
    </button>

    <!-- Logo -->
    <div class="logo-section">
      <div class="logo-text">SICAM</div>
    </div>

    <!-- Navegación central -->
    <div class="nav-buttons">
      <!-- Segmentación -->
      <button
        class="nav-btn"
        :class="{ active: seccion === 'segmentacion' }"
        @click="$emit('change-section', 'segmentacion')"
      >
        <svg
          class="nav-icon"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path d="M2 12h4l3-9 5 18 3-9h5" />
        </svg>
        Segmentación
      </button>

      <!-- Caracterización con candado si no hay caso -->
      <div class="nav-btn-wrap">
        <button
          class="nav-btn"
          :class="{ active: seccion === 'caracterizacion', locked: !caseId }"
          @click="$emit('change-section', 'caracterizacion')"
        >
          <svg
            class="nav-icon"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="M21.21 15.89A10 10 0 1 1 8 2.83" />
            <path d="M22 12A10 10 0 0 0 12 2v10z" />
          </svg>
          Caracterización
          <svg
            v-if="!caseId"
            class="lock-icon"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
            <path d="M7 11V7a5 5 0 0 1 10 0v4" />
          </svg>
        </button>

        <!-- Tooltip candado -->
        <div v-if="!caseId" class="nav-tooltip">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
            <path d="M7 11V7a5 5 0 0 1 10 0v4" />
          </svg>
          Selecciona un caso primero
        </div>
      </div>

      <!-- Registro -->
      <button
        class="nav-btn"
        :class="{ active: seccion === 'registro' }"
        @click="$emit('change-section', 'registro')"
      >
        <svg
          class="nav-icon"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
          <polyline points="14 2 14 8 20 8" />
          <line x1="16" y1="13" x2="8" y2="13" />
          <line x1="16" y1="17" x2="8" y2="17" />
        </svg>
        Registro
      </button>
    </div>

    <!-- Acciones lado derecho -->
    <div class="topbar-actions">
      <!-- Chip de caso activo -->
      <div v-if="caseId" class="case-chip">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2" />
          <rect x="8" y="2" width="8" height="4" rx="1" />
        </svg>
        Caso {{ caseId }}
      </div>

      <!-- Notificaciones -->
      <button class="action-btn" title="Notificaciones">
        <span class="notification-dot"></span>
        <svg
          class="topbar-icon"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
          <path d="M13.73 21a2 2 0 0 1-3.46 0" />
        </svg>
      </button>

      <!-- Avatar del doctor con menú desplegable -->
      <div class="doctor-menu-wrap" v-if="doctor">
        <button
          class="doctor-avatar-btn"
          :class="{ active: menuOpen }"
          @click="menuOpen = !menuOpen"
        >
          <div class="doctor-avatar">
            {{ doctorInitials }}
          </div>
          <div class="doctor-info">
            <span class="doctor-name">{{ doctor.nombre }} {{ doctor.apellido }}</span>
            <span class="doctor-role">{{ doctor.especialidad_display || "Doctor" }}</span>
          </div>
          <svg
            class="chevron"
            :class="{ rotated: menuOpen }"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <polyline points="6 9 12 15 18 9" />
          </svg>
        </button>

        <!-- Menú desplegable -->
        <transition name="menu-drop">
          <div v-if="menuOpen" class="doctor-dropdown">
            <!-- Cabecera con info del doctor -->
            <div class="dropdown-header">
              <div class="dropdown-avatar">{{ doctorInitials }}</div>
              <div class="dropdown-header-info">
                <div class="dropdown-name">
                  {{ doctor.nombre_completo || `Dr. ${doctor.nombre} ${doctor.apellido}` }}
                </div>
                <div class="dropdown-email">{{ doctor.email }}</div>
              </div>
            </div>

            <div class="dropdown-divider"></div>

            <button class="dropdown-item">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                <circle cx="12" cy="7" r="4" />
              </svg>
              Mi perfil
            </button>

            <button class="dropdown-item">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="3" />
                <path
                  d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83
                         l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21
                         a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33
                         l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15
                         a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9
                         a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06
                         A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0
                         v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06
                         a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9
                         a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"
                />
              </svg>
              Configuración
            </button>

            <div class="dropdown-divider"></div>

            <button class="dropdown-item logout-item" @click="onLogout">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                <polyline points="16 17 21 12 16 7" />
                <line x1="21" y1="12" x2="9" y2="12" />
              </svg>
              Cerrar sesión
            </button>
          </div>
        </transition>
      </div>
    </div>
  </nav>
</template>

<script>
export default {
  name: "TopBar",

  props: {
    seccion: {
      type: String,
      required: true,
    },
    caseId: {
      type: [String, Number],
      default: null,
    },
    doctor: {
      type: Object,
      default: null,
    },
  },

  emits: ["change-section", "toggle-sidebar", "logout"],

  data() {
    return {
      menuOpen: false,
    };
  },

  computed: {
    doctorInitials() {
      if (!this.doctor) return "?";
      const inicial_nombre = (this.doctor.nombre || "").charAt(0).toUpperCase();
      const inicial_apellido = (this.doctor.apellido || "").charAt(0).toUpperCase();
      return `${inicial_nombre}${inicial_apellido}`;
    },
  },

  methods: {
    closeMenu() {
      this.menuOpen = false;
    },

    onLogout() {
      this.menuOpen = false;
      this.$emit("logout");
    },
  },
};
</script>

<style scoped>
/* ============================================================
   TOPBAR — contenedor principal
============================================================ */
.topbar {
  height: 60px;
  background: linear-gradient(to right, #ffffff 0%, #f8f9fa 100%);
  border-bottom: 2px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  position: relative;
  z-index: 100;
}

/* ============================================================
   LOGO
============================================================ */
.logo-section {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-text {
  font-weight: 700;
  font-size: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.5px;
}

/* ============================================================
   BOTONES DE NAVEGACIÓN
============================================================ */
.nav-buttons {
  display: flex;
  gap: 6px;
  flex: 1;
  justify-content: center;
  padding: 0 20px;
  align-items: center;
}

.nav-btn {
  background: transparent;
  border: 2px solid transparent;
  padding: 8px 18px;
  font-size: 14px;
  color: #666;
  cursor: pointer;
  border-radius: 10px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;
  position: relative;
  overflow: hidden;
}

.nav-btn:hover {
  background: #f0f4f8;
  color: #2c3e50;
  transform: translateY(-1px);
}

.nav-btn:hover .nav-icon {
  transform: scale(1.1);
}

.nav-btn.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #ffffff;
  font-weight: 600;
  border-color: transparent;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.nav-icon {
  width: 18px;
  height: 18px;
  transition: transform 0.3s ease;
}

/* ---- Estado bloqueado (sin caso seleccionado) ---- */
.nav-btn.locked {
  color: #aaa;
  border-color: #e8e8e8;
  background: #fafafa;
}

.nav-btn.locked:hover {
  background: #f5f0ff;
  color: #9c7dd4;
  border-color: #d4c5f0;
  transform: translateY(-1px);
}

.nav-btn.locked .lock-icon {
  opacity: 1;
  stroke: #9c7dd4;
}

.lock-icon {
  width: 13px;
  height: 13px;
  opacity: 0.5;
  margin-left: 2px;
}

/* ---- Tooltip del candado ---- */
.nav-btn-wrap {
  position: relative;
}

.nav-btn-wrap:hover .nav-tooltip {
  opacity: 1;
  transform: translateX(-50%) translateY(0);
}

.nav-tooltip {
  position: absolute;
  bottom: -38px;
  left: 50%;
  transform: translateX(-50%) translateY(-4px);
  background: #2c3e50;
  color: white;
  font-size: 11px;
  font-weight: 500;
  padding: 5px 10px;
  border-radius: 6px;
  white-space: nowrap;
  opacity: 0;
  transition: all 0.2s ease;
  pointer-events: none;
  z-index: 9999;
  display: flex;
  align-items: center;
  gap: 5px;
}

.nav-tooltip svg {
  width: 11px;
  height: 11px;
}

.nav-tooltip::before {
  content: "";
  position: absolute;
  top: -4px;
  left: 50%;
  transform: translateX(-50%);
  border: 4px solid transparent;
  border-bottom-color: #2c3e50;
  border-top: 0;
}

/* ============================================================
   ACCIONES LADO DERECHO
============================================================ */
.topbar-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

/* ---- Chip de caso activo ---- */
.case-chip {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 11px;
  font-weight: 600;
  color: #667eea;
  background: #eef2ff;
  border: 1px solid #c7d2fe;
  border-radius: 20px;
  padding: 4px 10px;
  animation: fadeIn 0.3s ease;
}

.case-chip svg {
  width: 12px;
  height: 12px;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* ---- Botón de notificaciones ---- */
.action-btn {
  width: 36px;
  height: 36px;
  border: 2px solid #e0e0e0;
  background: white;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  position: relative;
  color: #666;
}

.action-btn:hover {
  background: #f0f4f8;
  border-color: #1e88e5;
  color: #1e88e5;
  transform: translateY(-1px);
}

.topbar-icon {
  width: 18px;
  height: 18px;
}

.notification-dot {
  position: absolute;
  top: 6px;
  right: 6px;
  width: 8px;
  height: 8px;
  background: #ef5350;
  border-radius: 50%;
  border: 2px solid white;
}

/* ============================================================
   AVATAR DEL DOCTOR
============================================================ */
.doctor-menu-wrap {
  position: relative;
}

.doctor-avatar-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  background: transparent;
  border: 1.5px solid #e0e0e0;
  border-radius: 10px;
  padding: 5px 10px 5px 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #2c3e50;
}

.doctor-avatar-btn:hover,
.doctor-avatar-btn.active {
  background: #f0f4f8;
  border-color: #667eea;
}

.doctor-avatar {
  width: 30px;
  height: 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  letter-spacing: 0.5px;
}

.doctor-info {
  display: flex;
  flex-direction: column;
  text-align: left;
}

.doctor-name {
  font-size: 12px;
  font-weight: 600;
  color: #2c3e50;
  line-height: 1.2;
  white-space: nowrap;
}

.doctor-role {
  font-size: 10px;
  color: #9ca3af;
  line-height: 1.2;
  white-space: nowrap;
}

.chevron {
  width: 14px;
  height: 14px;
  stroke: #9ca3af;
  transition: transform 0.2s ease;
}

.chevron.rotated {
  transform: rotate(180deg);
}

/* ============================================================
   DROPDOWN DEL DOCTOR
============================================================ */
.doctor-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  width: 240px;
  box-shadow:
    0 8px 32px rgba(0, 0, 0, 0.12),
    0 2px 8px rgba(0, 0, 0, 0.06);
  overflow: hidden;
  z-index: 9999;
}

.dropdown-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 16px;
  background: #fafbff;
}

.dropdown-avatar {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.dropdown-header-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.dropdown-name {
  font-size: 13px;
  font-weight: 600;
  color: #1a202c;
}

.dropdown-email {
  font-size: 11px;
  color: #9ca3af;
}

.dropdown-divider {
  height: 1px;
  background: #f0f0f0;
  margin: 4px 0;
}

.dropdown-item {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 9px 16px;
  background: none;
  border: none;
  font-size: 13px;
  color: #374151;
  cursor: pointer;
  text-align: left;
  transition: background 0.15s;
}

.dropdown-item:hover {
  background: #f8f9ff;
}

.dropdown-item svg {
  width: 15px;
  height: 15px;
  stroke: #9ca3af;
  flex-shrink: 0;
}

.logout-item {
  color: #dc2626;
}

.logout-item:hover {
  background: #fff5f5;
}

.logout-item svg {
  stroke: #dc2626;
}

/* ---- Animación del dropdown ---- */
.menu-drop-enter-active {
  transition: all 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.menu-drop-leave-active {
  transition: all 0.15s ease;
}

.menu-drop-enter-from,
.menu-drop-leave-to {
  opacity: 0;
  transform: translateY(-6px) scale(0.97);
}

/* ============================================================
   MENÚ HAMBURGUESA (solo mobile)
============================================================ */
.menu-btn {
  display: none;
  background: transparent;
  border: none;
  cursor: pointer;
  margin-right: 10px;
  color: #2c3e50;
  padding: 4px;
}

/* ============================================================
   RESPONSIVE
============================================================ */
@media (max-width: 1200px) {
  .topbar {
    padding: 0 12px;
  }

  .menu-btn {
    display: block;
  }

  .logo-text {
    font-size: 16px;
  }

  .nav-buttons {
    gap: 4px;
  }

  .nav-btn {
    padding: 8px 10px;
    font-size: 0; /* oculta el texto, solo muestra el ícono */
  }

  .case-chip {
    display: none;
  }

  .doctor-info {
    display: none;
  }

  .doctor-avatar-btn {
    padding: 5px;
  }
}
</style>
