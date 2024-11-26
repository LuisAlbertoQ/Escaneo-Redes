import nmap
from rest_framework.views import APIView
from django.db.models import Count
from rest_framework.response import Response
from rest_framework import status
from .models import Escaneo, Dispositivo
from .serializers import EscaneoSerializer, EscaneoSerializerHistory
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
            if 'hostscript' in nm_data:
                for script in nm_data['hostscript']:
                    if script.get('id') == 'smb-os-discovery':
                        nombre = script.get('output', '').split('\n')[0]
                        break

        return nombre if nombre else 'Sin nombre'

    def post(self, request):
        # IPs predeterminadas para el escaneo
        ips_disponibles = [
            "192.168.56.0/24",
            "172.23.160.0/20",
            "172.22.13.0/26",
            "172.23.160.0/20",
            "172.22.1.0/26",
            "10.80.96.0/21"
        ]

        # Obtiene el rango proporcionado por el usuario
        rango_ips = request.data.get('rango_ips', None)

        # Si no se proporciona, usar todas las disponibles
        if not rango_ips:
            rango_ips = ips_disponibles
        elif not isinstance(rango_ips, str) or '/' not in rango_ips:
            return Response({"error": "El rango de IPs no es válido. Usa el formato CIDR (ej: 192.168.1.0/24)."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Inicializar nmap
        nm = nmap.PortScanner()

        try:
            # Ejecutar el escaneo
            resultado = nm.scan(
                hosts=rango_ips if isinstance(rango_ips, str) else ",".join(rango_ips),
                arguments='-Pn -sS -O -sV --script nbstat.nse,smb-os-discovery.nse'
            )
        except Exception as e:
            return Response({"error": f"Error al ejecutar el escaneo: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Crear un registro de escaneo
        escaneo = Escaneo.objects.create(rango_ips=rango_ips if isinstance(rango_ips, str) else ",".join(ips_disponibles))
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

        # Serializar el escaneo y devolver los datos
        serializer = EscaneoSerializer(escaneo)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def clasificar_dispositivo(self, so, datos):
        """
        Clasificación más detallada del tipo de dispositivo.
        """
        so_lower = so.lower()
        servicios = datos.get('tcp', {})

        # Clasificar por puertos y servicios
        if any(port in servicios for port in [80, 443, 8080]) and \
           any('nginx' in str(servicios[port]).lower() or 'apache' in str(servicios[port]).lower() 
               for port in servicios):
            return 'Servidor Web'
        if 3306 in servicios or 5432 in servicios:
            return 'Servidor BD'
        if 21 in servicios or 22 in servicios:
            return 'Servidor FTP/SSH'

        # Clasificar por sistema operativo
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

class EscaneoGraficosAPIView(APIView):
    def get(self, request, escaneo_id):
        # Datos agregados por tipo
        por_tipo = Dispositivo.objects.filter(escaneo_id=escaneo_id).values('tipo').annotate(total=Count('tipo'))

        # Estados (activo/inactivo)
        por_estado = Dispositivo.objects.filter(escaneo_id=escaneo_id).values('estado').annotate(total=Count('estado'))

        # Sistemas operativos
        por_so = Dispositivo.objects.filter(escaneo_id=escaneo_id).values('sistema_operativo').annotate(total=Count('sistema_operativo'))

        # Fabricantes
        por_fabricante = Dispositivo.objects.filter(escaneo_id=escaneo_id).values('fabricante').annotate(total=Count('fabricante'))

        return Response({
            'por_tipo': list(por_tipo),
            'por_estado': list(por_estado),
            'por_so': list(por_so),
            'por_fabricante': list(por_fabricante),
        })

class HistorialEscaneosView(APIView):
    def get(self, request):
        escaneos = Escaneo.objects.all().order_by('-fecha_hora')  # Ordenar por fecha descendente
        serializer = EscaneoSerializerHistory(escaneos, many=True)
        return Response(serializer.data)