from django.db import models

class Escaneo(models.Model):
    fecha_hora = models.DateTimeField(auto_now_add=True)
    rango_ips = models.CharField(max_length=100)

    def __str__(self):
        return f"Escaneo {self.id} - {self.fecha_hora}"

class Dispositivo(models.Model):
    escaneo = models.ForeignKey(Escaneo, related_name='dispositivos', on_delete=models.CASCADE)
    ip = models.GenericIPAddressField()
    mac = models.CharField(max_length=50, blank=True, null=True)
    nombre = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=10, choices=[('Activo', 'Activo'), ('Inactivo', 'Inactivo')])
    sistema_operativo = models.CharField(max_length=100, blank=True, null=True)  # Nuevo campo
    fabricante = models.CharField(max_length=100, blank=True, null=True)  # Nuevo campo
    tipo = models.CharField(
        max_length=20,
        choices=[('PC', 'PC'), ('Móvil', 'Móvil'), ('Otro', 'Otro')],
        default='Otro'
    )  # Nuevo campo

    def __str__(self):
        return f"{self.ip} ({self.tipo})"
