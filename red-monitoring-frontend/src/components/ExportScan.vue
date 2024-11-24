<template>
    <div class="export-container">
        <b-button
            variant="success"
            @click="exportScan"
            :disabled="loading"
            class="d-flex align-items-center justify-content-center gap-2"
        >
            <b-spinner small v-if="loading"></b-spinner>
            <i class="bi bi-file-earmark-excel-fill me-2"></i>
            {{ loading ? "Generando Archivo..." : "Exportar a Excel" }}
        </b-button>

        <b-alert
            v-if="error"
            variant="danger"
            show
            dismissible
            class="mt-3"
            @dismissed="error = null"
        >
            {{ error }}
        </b-alert>
    </div>
</template>

<script>
import axios from "axios";

export default {
    name: 'ExportScan',
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
                        responseType: "blob",
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

                // Limpiar el URL creado
                window.URL.revokeObjectURL(url);
            } catch (err) {
                this.error = "No se pudo generar el archivo. Por favor, inténtalo de nuevo.";
                console.error('Error al exportar:', err);
            } finally {
                this.loading = false;
            }
        },
    },
};
</script>

<style scoped>
.export-container {
    display: flex;
    flex-direction: column;
    align-items: center;
}

.btn-success {
    min-width: 200px;
    padding: 0.75rem 1.5rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    transition: all 0.3s ease;
}

.btn-success:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.btn-success:disabled {
    cursor: not-allowed;
    opacity: 0.7;
}

.gap-2 {
    gap: 0.5rem;
}
</style>