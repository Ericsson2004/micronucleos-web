<template>
  <nav class="topbar">
    <div class="logo">MicroScan</div>

    <div class="nav-buttons">

      <button
        class="nav-btn"
        :class="{ active: seccion === 'segmentacion' }"
        @click="$emit('change-section', 'segmentacion')"
      >
        Segmentacion
      </button>

      <button
        class="nav-btn"
        :class="{ active: seccion === 'caracterizacion' }"
        @click="$emit('change-section', 'caracterizacion')"
      >
        Caracterización
      </button>
      
      <button
        class="nav-btn"
        :class="{ active: seccion === 'analisis' }"
        @click="$emit('change-section', 'analisis')"
      >
        Analisis
      </button>

      <!-- BOTÓN REGISTRO -->
      <button
        class="nav-btn"
        :class="{ active: seccion === 'registro' }"
        @click="$emit('change-section', 'registro')"
      >
        📝 Registro
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