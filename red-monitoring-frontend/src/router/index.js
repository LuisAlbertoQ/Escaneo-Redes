import { createRouter, createWebHistory } from 'vue-router'
import Home from "@/views/HomeS.vue"
import HistorialScreen from "@/components/HistorialScreen.vue";

const routes = [
    {
        path: "/",
        name: "Home",
        component: Home,
    },
    {
        path: '/charts/:escaneoId',
        name: 'ChartsScreen',
        component: () => import('@/components/ChartsScreen.vue'),
    },
    {
        path: "/historial",
        name: "HistorialScreen",
        component: HistorialScreen,
    },
]

const router = createRouter({
    history: createWebHistory(process.env.BASE_URL),
    routes
})

export default router