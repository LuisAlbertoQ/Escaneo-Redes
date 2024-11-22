import nmap
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Escaneo, Dispositivo
from .serializers import EscaneoSerializer
from openpyxl import Workbook
from django.http import HttpResponse

class EscanearRedView(APIView):
    def post(self, request):
        rango_ips = request.data.get('rango_ips', '192.168.1.0/24')  # Rango por defecto
        nm = nmap.PortScanner()

        try:
            # Ejecutar escaneo con análisis de puertos y detección de SO
            resultado = nm.scan(hosts=rango_ips, arguments='-sS -O')
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Crear registro de escaneo
        escaneo = Escaneo.objects.create(rango_ips=rango_ips)
        
        # Procesar resultados
        dispositivos = []
        for host, datos in resultado['scan'].items():
            # Obtener información básica
            ip = host
            mac = datos.get('addresses', {}).get('mac', '')
            nombre = datos.get('hostnames', [{}])[0].get('name', '')
            estado = 'Activo' if datos.get('status', {}).get('state') == 'up' else 'Inactivo'

            # Detección de SO
            osmatch = datos.get('osmatch', [])
            if osmatch:
                so = osmatch[0].get('name', 'Desconocido')
            else:
                so = 'Desconocido'

            # Fabricante
            fabricante = datos.get('vendor', {}).get(mac, 'Desconocido')

            # Clasificación del dispositivo
            tipo_dispositivo = 'Otro'
            if 'windows' in so.lower():
                tipo_dispositivo = 'PC'
            elif 'android' in so.lower() or 'ios' in so.lower():
                tipo_dispositivo = 'Móvil'

            # Crear dispositivo
            dispositivo = Dispositivo.objects.create(
                escaneo=escaneo,
                ip=ip,
                mac=mac,
                nombre=nombre,
                estado=estado,
                sistema_operativo=so,
                fabricante=fabricante,
                tipo=tipo_dispositivo
            )
            dispositivos.append(dispositivo)

        serializer = EscaneoSerializer(escaneo)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class ExportarEscaneoView(APIView):
    def get(self, request, escaneo_id):
        try:
            # Obtener el escaneo y sus dispositivos relacionados
            escaneo = Escaneo.objects.get(id=escaneo_id)
            dispositivos = escaneo.dispositivos.all()

            # Crear un archivo Excel
            wb = Workbook()
            ws = wb.active
            ws.title = "Resultados del Escaneo"

            # Encabezados
            ws.append([
                "IP", "MAC", "Nombre", "Estado", "Sistema Operativo", 
                "Fabricante", "Tipo de Dispositivo"
            ])

            # Agregar datos de los dispositivos
            for dispositivo in dispositivos:
                ws.append([
                    dispositivo.ip,
                    dispositivo.mac,
                    dispositivo.nombre,
                    dispositivo.estado,
                    dispositivo.sistema_operativo,
                    dispositivo.fabricante,
                    dispositivo.tipo
                ])

            # Crear la respuesta HTTP con el archivo Excel
            response = HttpResponse(
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            response["Content-Disposition"] = f"attachment; filename=escaneo_{escaneo_id}.xlsx"
            wb.save(response)

            return response

        except Escaneo.DoesNotExist:
            return Response(
                {"error": "El escaneo especificado no existe."},
                status=status.HTTP_404_NOT_FOUND
            )

