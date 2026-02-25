<template>
  <nav class="topbar">
    <button class="menu-btn" @click="$emit('toggle-sidebar')">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <line x1="3" y1="12" x2="21" y2="12"></line>
        <line x1="3" y1="6" x2="21" y2="6"></line>
        <line x1="3" y1="18" x2="21" y2="18"></line>
      </svg>
    </button>

    <div class="logo-section">
      <div class="logo-text">SICAM</div>
    </div>

    <div class="nav-buttons">
      <button
        class="nav-btn"
        :class="{ active: seccion === 'segmentacion' }"
        @click="$emit('change-section', 'segmentacion')"
      >
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M2 12h4l3-9 5 18 3-9h5"></path>
        </svg>
        Segmentación
      </button>

      <button
        class="nav-btn"
        :class="{ active: seccion === 'caracterizacion' }"
        @click="$emit('change-section', 'caracterizacion')"
      >
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21.21 15.89A10 10 0 1 1 8 2.83"></path>
          <path d="M22 12A10 10 0 0 0 12 2v10z"></path>
        </svg>
        Caracterización
      </button>

      <button
        class="nav-btn"
        :class="{ active: seccion === 'analisis' }"
        @click="$emit('change-section', 'analisis')"
      >
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>
        Análisis
      </button>

      <button
        class="nav-btn"
        :class="{ active: seccion === 'registro' }"
        @click="$emit('change-section', 'registro')"
      >
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
          <polyline points="14 2 14 8 20 8"></polyline>
          <line x1="16" y1="13" x2="8" y2="13"></line>
          <line x1="16" y1="17" x2="8" y2="17"></line>
          <polyline points="10 9 9 9 8 9"></polyline>
        </svg>
        Registro
      </button>
    </div>

    <div class="topbar-actions">
      <button class="action-btn" title="Notificaciones">
        <span class="notification-dot"></span>
        <svg class="topbar-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
          <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
        </svg>
      </button>
      <button class="action-btn" title="Configuración">
        <svg class="topbar-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="3"></circle>
          <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
        </svg>
      </button>
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
  },
};
</script>

<style scoped>
.topbar {
  height: 60px;
  background: linear-gradient(to right, #ffffff 0%, #f8f9fa 100%);
  border-bottom: 2px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

/* LOGO */
.logo-section {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-icon {
  font-size: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
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

/* NAVEGACIÓN */
.nav-buttons {
  display: flex;
  gap: 6px;
  flex: 1;
  justify-content: center;
  padding: 0 20px;
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

.nav-icon {
  width: 18px; /* Tamaño del SVG */
  height: 18px;
  transition: transform 0.3s ease;
}

.nav-btn.active .nav-icon {
  animation: bounce 0.5s ease;
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

.nav-btn.active .nav-icon {
  animation: bounce 0.5s ease;
}

@keyframes bounce {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.2); }
}

/* ACCIONES */
.topbar-actions {
  display: flex;
  gap: 8px;
}

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

.menu-btn {
  display: none;
  background: transparent;
  border: none;
  cursor: pointer;
  margin-right: 10px;
  color: #2c3e50;
  padding: 4px;
}

/* TABLET */
@media (max-width: 1200px) {
  .menu-btn {
    display: block;
  }
}

@media (max-width: 1200px) {
  .nav-btn {
    padding: 8px 10px;
    font-size: 0;
  }

  .nav-icon {
    font-size: 18px;
  }

  .nav-buttons {
    gap: 4px;
  }
}

@media (max-width: 1200px) {
  .topbar {
    padding: 0 12px;
  }

  .logo-text {
    font-size: 16px;
  }
}
</style>
