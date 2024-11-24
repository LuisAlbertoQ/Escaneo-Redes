<template>
    <div class="container py-4">
        <div class="card shadow-lg">
            <div class="card-header bg-primary text-white">
                <h1 class="h3 mb-0">Escaneo de Red</h1>
            </div>

            <div class="card-body">
                <b-form @submit.prevent="startScan" class="mb-4">
                    <b-form-group label="Rango de IP:" label-for="ipRange"
                        description="Ejemplo: 192.168.1.1-192.168.1.254">
                        <b-form-input id="ipRange" v-model="ipRange" placeholder="Ingrese el rango de IP"
                            :disabled="loading" trim></b-form-input>
                    </b-form-group>

                    <b-button type="submit" variant="primary" :disabled="loading" class="w-100">
                        <b-spinner small v-if="loading"></b-spinner>
                        {{ loading ? "Escaneando..." : "Iniciar Escaneo" }}
                    </b-button>
                </b-form>

                <b-alert v-if="error" variant="danger" show dismissible @dismissed="error = null">
                    {{ error }}
                </b-alert>

                <div v-if="devices.length > 0">
                    <h2 class="h4 mb-3">Resultados del Escaneo</h2>
                    <div class="table-responsive">
                        <b-table :items="devices" :fields="fields" striped hover responsive class="mb-4"></b-table>
                    </div>

                    <ExportScan v-if="escaneoId" :escaneoId="escaneoId" class="mt-3" />
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import axios from "axios";
import ExportScan from "@/components/ExportScan";

export default {
    name: 'NetworkScan',
    components: {
        ExportScan,
    },
    data() {
        return {
            ipRange: "",
            loading: false,
            error: null,
            devices: [],
            escaneoId: null,
            fields: [
                { key: 'ip', label: 'IP', sortable: true },
                { key: 'mac', label: 'MAC', sortable: true },
                { key: 'nombre', label: 'Nombre', sortable: true },
                {
                    key: 'estado',
                    label: 'Estado',
                    formatter: value => value ? 'Activo' : 'Inactivo',
                    tdClass: value => value ? 'text-success' : 'text-danger'
                },
                { key: 'sistema_operativo', label: 'Sistema Operativo' },
                { key: 'fabricante', label: 'Fabricante' },
                { key: 'tipo', label: 'Tipo' }
            ]
        };
    },
    methods: {
        async startScan() {
            this.error = null;
            this.devices = [];
            this.escaneoId = null;

            if (!this.ipRange) {
                this.error = "Por favor, ingresa un rango de IP válido.";
                return;
            }

            this.loading = true;
            try {
                const response = await axios.post("http://127.0.0.1:8000/api/monitor/escanear/", {
                    ip_range: this.ipRange,
                });
                this.devices = response.data.dispositivos;
                this.escaneoId = response.data.id;
            } catch (err) {
                this.error = err.response?.data?.error || "Ocurrió un error al escanear.";
            } finally {
                this.loading = false;
            }
        },
    },
};
</script>

<style scoped>
.card {
    border: none;
    border-radius: 0.5rem;
}

.card-header {
    border-radius: 0.5rem 0.5rem 0 0 !important;
}

.table-responsive {
    border-radius: 0.25rem;
}

.btn-primary {
    padding: 0.75rem;
    font-weight: 500;
}

@media (max-width: 768px) {
    .container {
        padding: 1rem;
    }
}
</style>