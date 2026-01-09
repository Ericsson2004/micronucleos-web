<template>
  <div class="dev-container">
    <h2>Registro de Análisis (Modo Desarrollo)</h2>

    <form @submit.prevent="submitForm">

      <!-- DATOS DEL ANÁLISIS -->
      <fieldset>
        <legend>Datos del Análisis</legend>

        <label>
          ID Paciente
          <input type="number" v-model="form.id_paciente_fk" required />
        </label>

        <label>
          ID Caso
          <input type="number" v-model="form.id_caso_fk" required />
        </label>
      </fieldset>

      <!-- MUESTRA DE SALIVA -->
      <fieldset>
        <legend>Muestra de Saliva</legend>

        <label>
          Imagen de la muestra
          <input type="file" @change="onMuestraChange" required />
        </label>
      </fieldset>

      <!-- RESULTADOS -->
      <fieldset>
        <legend>Resultado del Análisis</legend>

        <label>
          Núcleos
          <input type="number" v-model="form.nucleos" required />
        </label>

        <label>
          Micronúcleos
          <input type="number" v-model="form.micronucleos" required />
        </label>

        <label>
          Membranas
          <input type="number" v-model="form.membranas" required />
        </label>
      </fieldset>

      <!-- MÁSCARA (OPCIONAL) -->
      <fieldset>
        <legend>Máscara (opcional)</legend>

        <label>
          Tipo de máscara
          <input type="text" v-model="form.tipo_mascara" />
        </label>

        <label>
          Algoritmo
          <input type="text" v-model="form.algoritmo" />
        </label>

        <label>
          Imagen de la máscara
          <input type="file" @change="onMascaraChange" />
        </label>
      </fieldset>

      <button type="submit">Guardar análisis</button>
    </form>
  </div>
</template>

<script>
export default {
  name: "CargaAnalisis",
  data() {
    return {
      form: {
        id_paciente_fk: "",
        id_caso_fk: "",
        muestra_imagen: null,
        nucleos: "",
        micronucleos: "",
        membranas: "",
        tipo_mascara: "",
        algoritmo: "",
        mascara_imagen: null,
      },
    };
  },
  methods: {
    onMuestraChange(e) {
      this.form.muestra_imagen = e.target.files[0];
    },

    onMascaraChange(e) {
      this.form.mascara_imagen = e.target.files[0];
    },

    resetForm() {
      this.form = {
        id_paciente_fk: "",
        id_caso_fk: "",
        muestra_imagen: null,
        nucleos: "",
        micronucleos: "",
        membranas: "",
        tipo_mascara: "",
        algoritmo: "",
        mascara_imagen: null,
      };
    },

    async submitForm() {
      try {
        const formData = new FormData();

        // Datos del análisis
        formData.append("id_paciente_fk", this.form.id_paciente_fk);
        formData.append("id_caso_fk", this.form.id_caso_fk);

        // Imagen muestra
        formData.append("muestra_imagen", this.form.muestra_imagen);

        // Resultados
        formData.append("nucleos", this.form.nucleos);
        formData.append("micronucleos", this.form.micronucleos);
        formData.append("membranas", this.form.membranas);

        // Máscara (opcional)
        if (this.form.mascara_imagen) {
          formData.append("tipo_mascara", this.form.tipo_mascara);
          formData.append("algoritmo", this.form.algoritmo);
          formData.append("mascara_imagen", this.form.mascara_imagen);
        }

        const response = await fetch(
          "http://localhost:8000/api/dev/cargar-analisis/",
          {
            method: "POST",
            body: formData,
          }
        );

        const data = await response.json();

        if (response.ok) {
          alert("Análisis guardado correctamente");
          this.resetForm();
        } else {
          alert("Error: " + JSON.stringify(data));
        }
      } catch (error) {
        console.error(error);
        alert("Error de conexión con el backend");
      }
    },
  },
};
</script>


<style scoped>
.dev-container {
  height: calc(100vh - 50px);
  overflow-y: auto;
  padding: 25px;
  max-width: 750px;
  margin: auto;
}

fieldset {
  border: 1px solid #ccc;
  padding: 15px;
  margin-bottom: 15px;
}

label {
  display: block;
  margin-bottom: 10px;
}

input {
  width: 100%;
  padding: 6px;
}

button {
  padding: 10px 18px;
  cursor: pointer;
}
</style>