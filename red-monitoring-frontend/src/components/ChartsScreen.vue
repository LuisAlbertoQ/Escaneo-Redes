<template>
    <div class="container py-4">
        <div class="card shadow-lg">
            <div class="card-header bg-info text-white">
                <h1 class="h3 mb-0">Gráficos del Escaneo</h1>
            </div>

            <div class="card-body">
                <div class="row">
                    <div class="col-md-6">
                        <h4>Dispositivos por Tipo</h4>
                        <canvas id="chartPorTipo"></canvas>
                    </div>
                    <div class="col-md-6">
                        <h4>Estados de los Dispositivos</h4>
                        <canvas id="chartPorEstado"></canvas>
                    </div>
                    <div class="col-md-6">
                        <h4>Sistemas Operativos</h4>
                        <canvas id="chartPorSO"></canvas>
                    </div>
                    <div class="col-md-6">
                        <h4>Fabricantes</h4>
                        <canvas id="chartPorFabricante"></canvas>
                    </div>
                </div>
                <ExportScan v-if="escaneoId" :escaneoId="escaneoId" />
            </div>
        </div>
    </div>
</template>

<script>
import axios from "axios";
import { Chart, registerables } from "chart.js";
import ExportScan from "@/components/ExportScan";

Chart.register(...registerables);

export default {
    components: {
        ExportScan,
    },
    data() {
        return {
            escaneoId: this.$route.params.escaneoId,
        };
    },
    async mounted() {
        try {
            const response = await axios.get(`http://127.0.0.1:8000/api/monitor/graficos/${this.escaneoId}/`);
            const data = response.data;

            this.renderChart("chartPorTipo", "line", data.por_tipo, "Dispositivos por Tipo");
            this.renderChart("chartPorEstado", "doughnut", data.por_estado, "Estados de los Dispositivos");
            this.renderChart("chartPorSO", "polarArea", data.por_so, "Sistemas Operativos");
            this.renderChart("chartPorFabricante", "radar", data.por_fabricante, "Fabricantes");
        } catch (error) {
            console.error("Error al cargar datos para gráficos:", error);
        }
    },
    methods: {
        renderChart(canvasId, type, data, label) {
            const ctx = document.getElementById(canvasId).getContext("2d");
            new Chart(ctx, {
                type: type,
                data: {
                    labels: data.map(item => item.tipo || item.estado || item.sistema_operativo || item.fabricante),
                    datasets: [
                        {
                            label: label,
                            data: data.map(item => item.total),
                            backgroundColor: [
                                "#FF6384",
                                "#36A2EB",
                                "#FFCE56",
                                "#4BC0C0",
                                "#9966FF",
                                "#FF9F40",
                            ],
                        },
                    ],
                },
                options: {
                    responsive: true,
                },
            });
        },
    },
};
</script>
