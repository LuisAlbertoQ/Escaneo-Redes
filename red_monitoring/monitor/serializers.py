from rest_framework import serializers
from .models import Escaneo, Dispositivo

class DispositivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dispositivo
        fields = '__all__'

class EscaneoSerializer(serializers.ModelSerializer):
    dispositivos = DispositivoSerializer(many=True, read_only=True)

    class Meta:
        model = Escaneo
        fields = '__all__'

class EscaneoSerializerHistory(serializers.ModelSerializer):
    #dispositivos = DispositivoSerializer(many=True, read_only=True)
    class Meta:
        model = Escaneo
        fields = '__all__'