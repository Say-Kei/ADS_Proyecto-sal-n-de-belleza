from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .services import ComisionServices
from .serializers import ReporteComisionTrabajadorSerializer

class ConsultarComisionesTrabajadorView(APIView):
    """
    Endpoint para que un trabajador consulte sus comisiones acumuladas.
    Soporta filtros opcionales por URL: ?estado=COMPLETADA&fecha_inicio=2026-10-01&fecha_fin=2026-10-31
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        trabajador = request.user  # Usuario autenticado que realiza la petición

        # Obtener parámetros opcionales de la URL (?param=valor)
        estado_filtro = request.query_params.get('estado', 'COMPLETADA')
        fecha_inicio = request.query_params.get('fecha_inicio', None)
        fecha_fin = request.query_params.get('fecha_fin', None)

        # 1. Llamada al servicio
        resultado_dict = ComisionServices.calcularLaComisiones(
            trabajador=trabajador,
            estados=estado_filtro,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )

        # 2. Formateo de la respuesta con el Serializer
        serializer = ReporteComisionTrabajadorSerializer(resultado_dict)
        return Response(serializer.data, status=status.HTTP_200_OK)

def index(request):
    return render (request, 'reservaglow/index.html')

def salones(request):
    return render(request, 'reservaglow/salones/salon_esencia/cliente/estructuras/inicio.html')

def salones_citas(request):
    return render (request, 'reservaglow/salones/salon_esencia/cliente/estructuras/citas.html')

def salones_servicios(request):
    return render (request, 'reservaglow/salones/salon_esencia/cliente/estructuras/servicios.html')

def salones_ubicacion(request):
    return render (request, 'reservaglow/salones/salon_esencia/cliente/estructuras/ubicacion.html')