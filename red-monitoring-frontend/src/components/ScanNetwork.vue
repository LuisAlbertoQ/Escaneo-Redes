<template>
    <div>
        <h1>Escaneo de Red</h1>
        <div>
            <label for="ipRange">Rango de IP:</label>
            <input v-model="ipRange" id="ipRange" placeholder="Ej: 192.168.1.1-192.168.1.254" />
        </div>
        <button @click="startScan" :disabled="loading">
            {{ loading ? "Escaneando..." : "Iniciar Escaneo" }}
        </button>

        <div v-if="error" class="error">
            <p>{{ error }}</p>
        </div>

        <div v-if="devices.length > 0" class="results">
            <h2>Resultados del Escaneo</h2>
            <table>
                <thead>
                    <tr>
                        <th>IP</th>
                        <th>MAC</th>
                        <th>Nombre</th>
                        <th>Estado</th>
                        <th>Sistema Operativo</th>
                        <th>Fabricante</th>
                        <th>Tipo</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="device in devices" :key="device.mac">
                        <td>{{ device.ip }}</td>
                        <td>{{ device.mac }}</td>
                        <td>{{ device.nombre }}</td>
                        <td>{{ device.estado }}</td>
                        <td>{{ device.sistema_operativo }}</td>
                        <td>{{ device.fabricante }}</td>
                        <td>{{ device.tipo }}</td>
                    </tr>
                </tbody>
            </table>

            <!-- Botón de Exportar -->
            <ExportScan v-if="escaneoId" :escaneoId="escaneoId" />
        </div>
    </div>
</template>

<script>
import axios from "axios";
import ExportScan from "@/components/ExportScan";

export default {
    data() {
        return {
            ipRange: "",
            loading: false,
            error: null,
            devices: [],
            escaneoId: null, // ID del escaneo generado
        };
    },
    components: {
        ExportScan,
    },
    methods: {
        async startScan() {
            this.error = null;
            this.devices = [];
            this.escaneoId = null; // Resetear el ID del escaneo
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
                this.escaneoId = response.data.id; // Obtener el ID del escaneo
            } catch (err) {
                this.error = err.response?.data?.error || "Ocurrió un error al escanear.";
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
}

.results {
    margin-top: 20px;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th,
td {
    border: 1px solid #ccc;
    padding: 8px;
    text-align: left;
}
</style>