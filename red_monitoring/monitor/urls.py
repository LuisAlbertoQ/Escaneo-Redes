from django.urls import path
from .views import EscanearRedView, ExportarEscaneoView

urlpatterns = [
    path('escanear/', EscanearRedView.as_view(), name='escanear-red'),
    path('exportar/<int:escaneo_id>/', ExportarEscaneoView.as_view(), name='exportar_escaneo'),

]
