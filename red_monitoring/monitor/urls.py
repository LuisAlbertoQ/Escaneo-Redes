from django.urls import path
from .views import EscanearRedView, ExportarEscaneoView, EscaneoGraficosAPIView, HistorialEscaneosView

urlpatterns = [
    path('escanear/', EscanearRedView.as_view(), name='escanear-red'),
    path('exportar/<int:escaneo_id>/', ExportarEscaneoView.as_view(), name='exportar_escaneo'),
    path('graficos/<int:escaneo_id>/', EscaneoGraficosAPIView.as_view(), name='escaneo_graficos'),
    path('historial/', HistorialEscaneosView.as_view(), name='historial-escaneos'),

]
