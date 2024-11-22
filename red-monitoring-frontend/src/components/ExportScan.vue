<template>
    <div>
        <button @click="exportScan" :disabled="loading">
            {{ loading ? "Generando Archivo..." : "Exportar a Excel" }}
        </button>
        <p v-if="error" class="error">{{ error }}</p>
    </div>
</template>

<script>
import axios from "axios";

export default {
    props: {
        escaneoId: {
            type: Number,
            required: true,
        },
    },
    data() {
        return {
            loading: false,
            error: null,
        };
    },
    methods: {
        async exportScan() {
            this.error = null;
            this.loading = true;
            try {
                const response = await axios.get(
                    `http://127.0.0.1:8000/api/monitor/exportar/${this.escaneoId}/`,
                    {
                        responseType: "blob", // Necesario para manejar archivos
                    }
                );

                // Crear un enlace para descargar el archivo
                const url = window.URL.createObjectURL(new Blob([response.data]));
                const link = document.createElement("a");
                link.href = url;
                link.setAttribute("download", `escaneo_${this.escaneoId}.xlsx`);
                document.body.appendChild(link);
                link.click();
                link.remove();
            } catch (err) {
                this.error = "No se pudo generar el archivo. Inténtalo de nuevo.";
            } finally {
                this.loading = false;
            }
        },
    },
};
</script>

<style>
.error {
    color: red;
    margin-top: 10px;
}
</style>