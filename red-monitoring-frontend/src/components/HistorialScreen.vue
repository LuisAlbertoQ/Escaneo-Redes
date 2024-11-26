<template>
    <div class="container py-4">
        <div class="card shadow-lg">
            <div class="card-header bg-primary text-white">
                <h1 class="h3 mb-0">Historial de Escaneos</h1>
            </div>
            <div class="card-body">
                <!-- Barra de búsqueda -->
                <b-form-group label="Buscar" label-for="search" class="mb-4">
                    <b-form-input id="search" v-model="searchQuery" placeholder="Buscar por rango de IP o fecha" trim />
                </b-form-group>

                <!-- Tabla de escaneos -->
                <b-table
                    :items="filteredEscaneos"
                    :fields="fields"
                    hover
                    responsive
                    :per-page="itemsPerPage"
                    :current-page="currentPage"
                >
                    <template #cell(acciones)="row">
                        <b-button variant="primary" size="sm" @click="verResultados(row.item.id)">
                            Ver Resultados
                        </b-button>
                    </template>
                </b-table>

                <!-- Paginación -->
                <b-pagination
                    v-model="currentPage"
                    :total-rows="filteredEscaneos.length"
                    :per-page="itemsPerPage"
                    align="center"
                    class="mt-3"
                ></b-pagination>
            </div>
        </div>
    </div>
</template>

<script>
import axios from "axios";

export default {
    name: "HistorialScreen",
    data() {
        return {
            escaneos: [],
            fields: [
                { key: "id", label: "ID", sortable: true },
                { key: "rango_ips", label: "Rango de IP" },
                { key: "fecha_hora", label: "Fecha", sortable: true },
                { key: "acciones", label: "Acciones" }
            ],
            searchQuery: "",
            currentPage: 1,
            itemsPerPage: 5, // Mostrar 5 elementos por página
        };
    },
    computed: {
        filteredEscaneos() {
            // Filtrar por rango de IP o fecha
            return this.escaneos.filter((escaneo) => {
                const search = this.searchQuery.toLowerCase();
                return (
                    escaneo.rango_ips.toLowerCase().includes(search) ||
                    escaneo.fecha_hora.toLowerCase().includes(search)
                );
            });
        },
    },
    async created() {
        try {
            const response = await axios.get("http://127.0.0.1:8000/api/monitor/historial/");
            this.escaneos = response.data;
        } catch (err) {
            console.error("Error al cargar el historial:", err);
        }
    },
    methods: {
        verResultados(escaneoId) {
            this.$router.push(`/charts/${escaneoId}`);
        },
    },
};
</script>
