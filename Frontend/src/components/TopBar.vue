<template>
  <nav class="topbar">
    <div class="logo">MicroScan</div>

    <div class="nav-buttons">

      <button
        class="nav-btn"
        :class="{ active: seccionActiva === 'analisis' }"
        @click="$emit('change-section', 'analisis')"
      >
        Análisis
      </button>

      <button
        class="nav-btn"
        :class="{ active: seccionActiva === 'segmentacion' }"
        @click="$emit('change-section', 'segmentacion')"
      >
        Segmentación
      </button>

      <button
        class="nav-btn"
        :class="{ active: seccionActiva === 'caracterizacion' }"
        @click="$emit('change-section', 'caracterizacion')"
      >
        Caracterización
      </button>

      <!-- BOTÓN DEV -->
      <button
        class="nav-btn dev"
        :class="{ active: seccionActiva === 'dev' }"
        @click="$emit('change-section', 'dev')"
      >
        DEV
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
  height: 50px;
  background: #ffffff;
  border-bottom: 1px solid #ddd;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
}

.logo {
  font-weight: 600;
  font-size: 16px;
}

.nav-buttons {
  display: flex;
  gap: 8px;
}

.nav-btn {
  background: transparent;
  border: none;
  padding: 6px 14px;
  font-size: 14px;
  color: #666;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.nav-btn:hover {
  background: #f0f4f8;
}

.nav-btn.active {
  background: #1e88e5;
  color: #ffffff;
  font-weight: 500;
}

.dev {
  color: #d32f2f;
  font-weight: 600;
}
</style>