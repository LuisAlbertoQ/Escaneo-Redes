<template>
    <div class="network-scan-container">
        <router-link to="/historial" class="btn btn-primary">
            Historial de Escaneos
        </router-link>
        <ScanNetwork />
        <nav class="mt-4">
        </nav>
    </div>
</template>

<script>
import ScanNetwork from "@/components/ScanNetwork";

export default {
    name: 'NetworkScanPage',
    components: {
        ScanNetwork,
    },
};
</script>

<style scoped>
.network-scan-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 20px;
}

.btn {
    text-decoration: none;
    padding: 10px 15px;
    border-radius: 5px;
    transition: background-color 0.3s ease;
}

.btn-primary {
    background-color: #007bff;
    color: white;
}

.btn-primary:hover {
    background-color: #0056b3;
}
</style>