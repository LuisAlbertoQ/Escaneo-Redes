import nmap
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Escaneo, Dispositivo
from .serializers import EscaneoSerializer
from openpyxl import Workbook
from django.http import HttpResponse
import socket
import subprocess

class EscanearRedView(APIView):
    def get_device_name(self, ip, nm_data):
        """
        Intenta obtener el nombre del dispositivo usando múltiples métodos.
        """
        nombre = None
        
        # Método 1: Intentar obtener el nombre desde nmap hostnames
        hostnames = nm_data.get('hostnames', [])
        if hostnames and isinstance(hostnames, list) and len(hostnames) > 0:
            for hostname in hostnames:
                if hostname.get('name') and hostname.get('name') != '':
                    nombre = hostname.get('name')
                    break

        # Método 2: Intentar resolución DNS inversa
        if not nombre or nombre == '':
            try:
                nombre = socket.gethostbyaddr(ip)[0]
            except (socket.herror, socket.gaierror):
                pass

        # Método 3: Intentar NetBIOS name (Windows)
        if not nombre or nombre == '':
            try:
                # Requiere que nbtscan esté instalado en el sistema
                result = subprocess.run(['nbtscan', '-q', ip], 
                                     capture_output=True, 
                                     text=True, 
                                     timeout=2)
                if result.stdout:
                    # Parsear la salida de nbtscan para extraer el nombre
                    parts = result.stdout.strip().split()
                    if len(parts) > 1:
                        nombre = parts[1]
            except (subprocess.SubprocessError, FileNotFoundError):
                pass

        # Método 4: Usar información adicional de nmap
        if not nombre or nombre == '':
            # Intentar obtener información desde los scripts NSE de nmap
            if 'hostscript' in nm_data:
                for script in nm_data['hostscript']:
                    if script.get('id') == 'smb-os-discovery':
                        nombre = script.get('output', '').split('\n')[0]
                        break

        return nombre if nombre else 'Sin nombre'

    def post(self, request):
        rango_ips = request.data.get('rango_ips', '192.168.1.0/24')

        if not isinstance(rango_ips, str) or '/' not in rango_ips:
            return Response({"error": "El rango de IPs no es válido. Usa el formato CIDR (ej: 192.168.1.0/24)."},
                          status=status.HTTP_400_BAD_REQUEST)

        nm = nmap.PortScanner()

        try:
            # Mejorado los argumentos de escaneo para obtener más información
            resultado = nm.scan(
                hosts=rango_ips,
                arguments='-sS -O -sV --script nbstat.nse,smb-os-discovery.nse'
            )
        except Exception as e:
            return Response({"error": f"Error al ejecutar el escaneo: {str(e)}"},
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        escaneo = Escaneo.objects.create(rango_ips=rango_ips)
        dispositivos = []

        for host, datos in resultado.get('scan', {}).items():
            ip = host
            mac = datos.get('addresses', {}).get('mac', '')
            estado = 'Activo' if datos.get('status', {}).get('state') == 'up' else 'Inactivo'

            # Usar el nuevo método para obtener el nombre
            nombre = self.get_device_name(ip, datos)

            # Detección de sistema operativo
            osmatch = datos.get('osmatch', [])
            so = osmatch[0].get('name', 'Desconocido') if osmatch else 'Desconocido'

            # Fabricante del dispositivo
            fabricante = datos.get('vendor', {}).get(mac, 'Desconocido')

            # Clasificación mejorada del tipo de dispositivo
            tipo_dispositivo = self.clasificar_dispositivo(so, datos)

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

    def clasificar_dispositivo(self, so, datos):
        """
        Clasificación más detallada del tipo de dispositivo
        """
        so_lower = so.lower()
        
        # Verificar servicios detectados
        servicios = datos.get('tcp', {})
        
        # Detectar dispositivos específicos por puertos y servicios
        if any(port in servicios for port in [80, 443, 8080]) and \
           any('nginx' in str(servicios[port]).lower() or 'apache' in str(servicios[port]).lower() 
               for port in servicios):
            return 'Servidor Web'
            
        if 3306 in servicios or 5432 in servicios:
            return 'Servidor BD'
            
        if 21 in servicios or 22 in servicios:
            return 'Servidor FTP/SSH'

        # Clasificación por sistema operativo
        if 'windows' in so_lower:
            return 'PC Windows'
        elif 'linux' in so_lower:
            return 'PC Linux'
        elif 'mac' in so_lower or 'darwin' in so_lower:
            return 'PC Mac'
        elif 'android' in so_lower:
            return 'Dispositivo Android'
        elif 'ios' in so_lower:
            return 'Dispositivo iOS'
        elif 'router' in so_lower or 'mikrotik' in so_lower or 'cisco' in so_lower:
            return 'Router'
        elif 'printer' in so_lower or any('printer' in str(service).lower() for service in servicios.values()):
            return 'Impresora'
            
        return 'Otro'
    
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

