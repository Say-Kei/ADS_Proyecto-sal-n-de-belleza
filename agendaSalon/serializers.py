"""Serializadores para la gestión y creación de citas del salón."""
from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist, ValidationError as DjangoValidationError
from .models import Cita, Servicio, Establecimiento, PerfilUsuario
from .services import CitaService, ServicioService

class CrearCitaSerializer(serializers.Serializer):
    establecimiento_uuid = serializers.UUIDField(
        write_only=True,
        help_text="UUID público del establecimiento/salón."
    )
    servicios_uuids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        allow_empty=False,
        help_text="Lista de UUIDs de los servicios seleccionados."
    )
    trabajador_uuid = serializers.UUIDField(
        write_only=True,
        required=False,
        allow_null=True,
        help_text="UUID del trabajador opcional si el cliente lo elige."
    )
    nombre_cliente = serializers.CharField(max_length=120)
    correo_cliente = serializers.EmailField()
    telefono_cliente = serializers.CharField(max_length=20)
    fecha_cita = serializers.DateField()
    hora_inicio = serializers.TimeField()
    nota = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    # CAMPOS DE SALIDA (Respuesta que se devuelve al cliente)

    codigo_unico = serializers.UUIDField(read_only=True)
    estado = serializers.CharField(read_only=True)
    fecha_expiracion = serializers.DateTimeField(read_only=True)
    detalles_pago = serializers.SerializerMethodField(read_only=True)

    # VALIDACIONES DE EXISTENCIA Y CONSULTA

    def validate(self, attrs):
        # 1. Validar y recuperar el Establecimiento por UUID
        try:
            establecimiento = Establecimiento.objects.get(
                codigo_unico=attrs['establecimiento_uuid'],
                estado=True
            )
        except ObjectDoesNotExist as exc:
            raise serializers.ValidationError({
                "establecimiento_uuid": 
                ("El establecimiento indicado no existe o se encuentra inactivo.")
            }) from exc

        # 2. Validar y recuperar la lista de Servicios por sus UUIDs
        servicios = list(Servicio.objects.filter(
            codigo_unico__in=attrs['servicios_uuids'],
            estado=True
        ))
        if len(servicios) != len(attrs['servicios_uuids']):
            raise serializers.ValidationError({
                "servicios_uuids": "Uno o más servicios seleccionados no existen o están inactivos."
            })

        # 3. Validar y recuperar el Trabajador opcional por UUID
        trabajador = None
        trabajador_uuid = attrs.get('trabajador_uuid')
        if trabajador_uuid:
            try:
                trabajador = PerfilUsuario.objects.get(
                    codigo_unico=trabajador_uuid,
                    estado=True
                )
            except ObjectDoesNotExist as exc:
                raise serializers.ValidationError({
                    "trabajador_uuid": "El profesional seleccionado no existe o no se encuentra activo."
                }) from exc

        # Guardar las instancias de modelos en el diccionario interno para el create()
        attrs['establecimiento_obj'] = establecimiento
        attrs['servicios_objs'] = servicios
        attrs['trabajador_obj'] = trabajador

        return attrs
    # CREACIÓN DELEGADA A LA CAPA DE SERVICIOS
    def create(self, validated_data):
        try:
            # Se invoca a CitaService pasando los objetos resueltos
            cita = CitaService.validarCitaPendiente(
                servicios=validated_data['servicios_objs'],
                establecimiento=validated_data['establecimiento_obj'],
                trabajador=validated_data['trabajador_obj'],
                fecha_cita=validated_data['fecha_cita'],
                hora_inicio=validated_data['hora_inicio'],
                nombre_cliente=validated_data['nombre_cliente'],
                correo=validated_data['correo_cliente'],
                telefono=validated_data['telefono_cliente'],
                notas=validated_data.get('nota')
            )
            return cita

        except DjangoValidationError as e:
            # Convierte las excepciones de negocio lanzadas por los servicios a errores HTTP 400 de DRF
            raise serializers.ValidationError({"error_negocio": e.messages})

    def get_detalles_pago(self, obj: Cita) -> dict:
        """
        Calcula y entrega los totales financieros a través de ServicioService.
        """
        servicios = list(obj.serviciof.all())
        totales = ServicioService.precioServicio(servicios)
        return {
            "monto_total": totales["suma_total"],
            "anticipo_30_porciento": totales["monto_anticipo"],
            "saldo_restante_salon": totales["monto_restante"],
            "duracion_total_minutos": totales["duracion_total_minutos"]
        }

    def update(self, instance, validated_data):
        raise NotImplementedError("Este serializador no soporta actualizaciones de citas.")

class CitaResumenComisionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cita
        fields = [
            'codigo_unico',
            'nombre_cliente',
            'fecha_cita',
            'hora_inicio',
            'estado'
        ]
class ReporteComisionTrabajadorSerializer(serializers.Serializer):# pylint: disable=abstract-method
    """
    Serializador de salida para mapear el diccionario retornado por
    ComisionServices.calcularLasComisiones.
    """
    trabajador_uuid = serializers.UUIDField(allow_null=True)
    nombre_trabajador = serializers.CharField()
    porcentaje_comision = serializers.DecimalField(max_digits=5, decimal_places=2)
    estados_consultados = serializers.ListField(child=serializers.CharField())
    monto_total_generado = serializers.DecimalField(max_digits=10, decimal_places=2)
    monto_comision = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_citas = serializers.IntegerField()
    citas = CitaResumenComisionSerializer(many=True)
