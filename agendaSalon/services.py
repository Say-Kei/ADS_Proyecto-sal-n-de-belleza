from datetime import datetime, timedelta  # operaciones
from decimal import Decimal
from django.utils import timezone  # tiene hora y zona horaria 
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import transaction
from typing import List, Union
from django.db.models import QuerySet
from django.contrib.auth import authenticate, password_validation
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .models import (
    Establecimiento,
    PerfilUsuario,
    Categoria,
    Servicio,
    Cita,
    Factura,
    FacturaDetalle,
    Resena,
    HorarioEstablecimiento,   # ahora se usa en validar_horario (días cerrados)
    HorarioTrabajador
)

from .permissions import (
    Rol,
    filtrar_query_por_user,
    obtener_establecimiento,
    obtener_perfil,
    obtener_rol,
)

class AuthService:
    """
    Todo lo relacionado con AUTENTICACIÓN (RF-01, RNF-03):
    iniciar sesión, registrar personal y cerrar sesión. El cliente NO se autentica.
 
    Se usan tokens JWT: al iniciar sesión el sistema entrega dos "pases":
      - access:  dura poco; se envía en cada petición para identificarse.
      - refresh: dura más; sirve para pedir un access nuevo sin volver a escribir la clave.
    """
 
    @staticmethod
    def auenticar_generar_tokens(username_o_email: str, password: str) -> dict:
        """Valida las credenciales y devuelve los tokens y los datos del usuario."""
        # Permite iniciar sesión con el usuario O con el correo.
        # Si lo escrito tiene '@', buscamos el usuario dueño de ese correo.
        username = username_o_email
        if '@' in username_o_email:
            user_obj = User.objects.filter(email__iexact=username_o_email).first()
            if user_obj:
                username = user_obj.username
 
        # authenticate() compara la contraseña con la versión encriptada guardada.
        # Devuelve el usuario si es correcta o None si no.
        user = authenticate(username=username, password=password)
        if not user:
            # Mensaje genérico a propósito: no revela si falló el usuario o la clave.
            raise ValidationError("Credenciales inválidas. Verifique su usuario/correo y contraseña.")
 
        if not user.is_active:
            raise PermissionDenied("Esta cuenta de usuario se encuentra desactivada.")
 
        # `fperfil` es el nombre con el que el User llega a su PerfilUsuario (ver models.py).
        # getattr(..., None) evita un error si el usuario no tiene perfil.
        perfil = getattr(user, 'fperfil', None)
        es_super = user.is_superuser or (perfil is not None and perfil.rol == Rol.SUPERADMIN)
 
        # El Superadmin no depende de ningún salón; todos los demás sí se validan.
        if not es_super:
            if perfil is None:
                raise PermissionDenied("El usuario no tiene un perfil configurado en el sistema.")
            if not perfil.estado:
                raise PermissionDenied("Su perfil de trabajo/administrador está inactivo.")
            # RN-11: si el salón está inactivo, nadie de ese salón puede entrar.
            if perfil.establecimientof and not perfil.establecimientof.estado:
                raise PermissionDenied(
                    "El acceso a este establecimiento se encuentra suspendido por falta de pago. "
                    "Contacte al administrador de la plataforma."
                )
 
        rol = str(Rol.SUPERADMIN) if es_super else perfil.rol
        # El Superadmin no tiene salón: aquí quedaría en None.
        establecimiento = perfil.establecimientof if perfil else None
        nombre_completo = user.get_full_name() or user.username
 
        # Se crean los tokens y se les agregan datos extra (los "claims"), para
        # que la API sepa el rol y el salón sin consultar la base de datos.
        refresh = RefreshToken.for_user(user)
        refresh['rol'] = rol
        refresh['establecimiento_id'] = establecimiento.pk if establecimiento else None
        refresh['nombre_completo'] = nombre_completo
 
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "usuario": {
                "id": user.pk,
                "username": user.username,
                "email": user.email,
                "nombre_completo": nombre_completo,
                "rol": rol,
                "establecimiento_id": establecimiento.pk if establecimiento else None,
                "nombre_establecimiento": establecimiento.nombre if establecimiento else 'Plataforma',
            }
        }
    # todo o nada: si algo falla, NO se guarda el usuario a medias
    @staticmethod
    @transaction.atomic    
    def registrar_personal(
        username: str,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        establecimiento: Establecimiento,
        rol: str,
        porcentaje_comision=Decimal('0.00'),
        telefono=None
    ) -> PerfilUsuario:
        """Da de alta a un ADMIN_NEGOCIO, ASISTENTE o TRABAJADOR en un establecimiento."""
        # El personal debe tener un rol de los que pertenecen a un salón.
        if rol not in PerfilUsuario.ROLES_CON_ESTABLECIMIENTO:
            raise ValidationError(
                f"El rol '{rol}' no es válido para el personal de un establecimiento."
            )
        if establecimiento is None:
            raise ValidationError("El personal debe pertenecer a un establecimiento.")
        # __iexact = comparar sin distinguir mayúsculas ("Ana" y "ana" son lo mismo).
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError(f"El nombre de usuario '{username}' ya está registrado.")
        if email and User.objects.filter(email__iexact=email).exists():
            raise ValidationError(f"El correo electrónico '{email}' ya se encuentra en uso.")
 
        # Valida la fortaleza de la contraseña con las reglas de settings.py
        # (largo mínimo, no demasiado común, etc.). RNF-03.
        # Se pasa un User de prueba (sin guardar) para detectar claves parecidas al usuario o al correo.
        candidato = User(username=username, email=email, first_name=first_name, last_name=last_name)
        password_validation.validate_password(password, candidato)
 
        # create_user guarda la contraseña ENCRIPTADA (hash), nunca en texto plano.
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        # Se crea el perfil con el rol y el salón. Al guardarse, PerfilUsuario.save()
        # valida el rol y ajusta is_staff automáticamente (ver models.py).
        return PerfilUsuario.objects.create(
            usuariof=user,
            establecimientof=establecimiento,
            rol=rol,
            porcentaje_comision=porcentaje_comision,
            telefono=telefono,
            estado=True
        )
 
    @staticmethod
    def cerrar_sesion(refresh_token_str: str) -> bool:
        """
        Cierra la sesión: agrega el refresh token a la "lista negra" (blacklist)
        para que nadie pueda usarlo otra vez, aunque todavía no haya expirado.
        """
        try:
            token = RefreshToken(refresh_token_str)
            token.blacklist()
            return True
        except TokenError as err:
            raise ValidationError("El token proporcionado no es válido o ya ha expirado.") from err
 

class ValidarService:
    @staticmethod
    def validar_multicliente(
            servicios: Union[Servicio, List[Servicio], QuerySet],
            establecimiento: Establecimiento,
            trabajador: PerfilUsuario = None,
    ) -> bool:

        if isinstance(servicios, Servicio):
            lista_servicios = [servicios]
        else:
            lista_servicios = list(servicios)
        if not lista_servicios:
            raise ValidationError("No se proporcionaron servicios para validar.")

        for servicio in lista_servicios:
            servicio_valido = Servicio.objects.filter(
                pk=servicio.pk,
                estado=True,
                categoriaf__estado=True,
                categoriaf__establecimientof=establecimiento
            ).exists()

            if not servicio_valido:
                nombre_servicio = getattr(servicio, 'nombre', 'desconocido')
                nombre_establecimiento = getattr(establecimiento, 'nombre', 'desconocido')
                raise ValidationError(
                    f"El servicio '{nombre_servicio}' no es válido para el establecimiento '{nombre_establecimiento}'."
                )

            if trabajador:
                asociacion_servicio_trabajador = servicio.trabajadoresf.filter(
                    pk=trabajador.pk,
                    estado=True
                ).exists()

                if not asociacion_servicio_trabajador:
                    nombre_servicio = getattr(servicio, 'nombre', 'desconocido')
                    raise ValidationError(
                        f"El trabajador no está capacitado para el servicio '{nombre_servicio}'."
                    )
        if trabajador:
            trabajador_valido=PerfilUsuario.objects.filter(
                pk=trabajador.pk,
                estado=True,
                establecimientof=establecimiento
            ).exists()

            if not trabajador_valido:
                nombre_establecimiento = getattr(establecimiento, 'nombre', 'desconocido')
                raise ValidationError(
                    f"El trabajador no pertenece al establecimiento '{nombre_establecimiento}'."
                )
        establecimiento_activo = Establecimiento.objects.filter(
            pk=establecimiento.pk,
            estado=True
        ).exists()

        if not establecimiento_activo:
            nombre_establecimiento = getattr(establecimiento, 'nombre', 'desconocido')
            raise ValidationError(
                f"El establecimiento '{nombre_establecimiento}' no está activo."
            )
        return True
    @staticmethod
    def validar_trabajadores(
            servicios: List[Servicio],
            establecimiento: Establecimiento,
            trabajador: PerfilUsuario = None,
            fecha_cita=None,
            hora_inicio=None,
    ) -> List[dict]:
        
        asignaciones = []
        revisar_disponibilidad = fecha_cita is not None and hora_inicio is not None

        #  el cliente eligió un trabajador 
        if trabajador:
            # Debe ser de este salón y estar activo (RN-08).
            if not PerfilUsuario.objects.filter(
                pk=trabajador.pk,
                estado=True,
                establecimientof=establecimiento
            ).exists():
                raise ValidationError(
                    f"El trabajador no pertenece al establecimiento '{establecimiento.nombre}'."
                )
            
            for serv in servicios:
                capacitado = serv.trabajadoresf.filter(
                    pk=trabajador.pk,
                    estado=True
                ).exists()
                if not capacitado:
                    raise ValidationError(
                        f"El trabajador no está capacitado para el servicio '{serv.nombre}'."
                    )
                asignaciones.append({'servicio': serv, 'trabajador': trabajador})

            return asignaciones

        #  UN solo trabajador que haga TODOS los servicios
        # 
        candidatos = PerfilUsuario.objects.filter(
            establecimientof=establecimiento,
            estado=True,
            rol=PerfilUsuario.RolChoices.TRABAJADOR,
        ).order_by('pk')

        for serv in servicios:
            candidatos = candidatos.filter(fservicios_asociados=serv)
        candidatos = list(candidatos)

        if candidatos:
            if revisar_disponibilidad:

                elegido = next(
                    (c for c in candidatos
                     if CitaService.secuencia_disponible(c, servicios, fecha_cita, hora_inicio)),
                    None
                )
                if elegido is None:
                    raise ValidationError(
                        "Ningún profesional capacitado para estos servicios está disponible "
                        "en el horario seleccionado. Pruebe con otra hora u otro día."
                    )
            else:
                elegido = candidatos[0]
            return [{'servicio': serv, 'trabajador': elegido} for serv in servicios]

        # ---- CASO 3: un especialista distinto por cada servicio -----------
        hora_bloque = hora_inicio
        for serv in servicios:
            capacitados = list(serv.trabajadoresf.filter(
                establecimientof=establecimiento,
                estado=True,
                rol=PerfilUsuario.RolChoices.TRABAJADOR,
            ).order_by('pk'))
            if not capacitados:
                raise ValidationError(
                    f"No hay ningún profesional capacitado para realizar el servicio '{serv.nombre}'."
                )

            if revisar_disponibilidad:
                # El primero que esté libre justo en el momento en que toca este servicio.
                especialista = next(
                    (c for c in capacitados
                     if CitaService.trabajador_disponible(c, fecha_cita, hora_bloque, serv.duracion_minutos)),
                    None
                )
                if especialista is None:
                    raise ValidationError(
                        f"No hay ningún profesional disponible para el servicio '{serv.nombre}' "
                        f"en el horario seleccionado."
                    )
                # Los servicios van uno tras otro: el siguiente empieza cuando termina este.
                hora_bloque = FechaCita.sumarMinutos(fecha_cita, hora_bloque, serv.duracion_minutos)
            else:
                especialista = capacitados[0]

            asignaciones.append({'servicio': serv, 'trabajador': especialista})
        return asignaciones

class ServicioService:

    porcentajeDeAnticipo = Decimal('0.30')  # 30% de anticipo por defecto

    @classmethod
    def precioServicio(
        cls,
        servicios: Union[List[Servicio], QuerySet],
        porcentajeDeAnticipo: Decimal = None
    ) -> dict:
        """
        Calcula la suma total de dinero, duraciones acumuladas en minutos,
        monto del anticipo (30%) y saldo restante (70%) para una lista de servicios.
        """
        if porcentajeDeAnticipo is None:
            porcentajeDeAnticipo = cls.porcentajeDeAnticipo

        if not servicios:
            return {
                "suma_total": Decimal('0.00'),
                "monto_anticipo": Decimal('0.00'),
                "monto_restante": Decimal('0.00'),
                "duracion_total_minutos": 0,
                "cantidad_servicios": 0
            }

        # 1. Sumar los precios de los servicios
        suma_total = sum(
            Decimal(str(getattr(s, 'precio', '0.00')))
            for s in servicios
        )

        # 2. Sumar la duración acumulada en minutos de todos los servicios
        duracion_total_minutos = sum(
            int(getattr(s, 'duracion_minutos', 0))
            for s in servicios
        )

        # 3. Cálculos de anticipo y saldo restante
        monto_anticipado = (suma_total * porcentajeDeAnticipo).quantize(Decimal('0.01'))
        monto_restante = suma_total - monto_anticipado

        return {
            "suma_total": suma_total,
            "monto_anticipo": monto_anticipado,
            "monto_restante": monto_restante,
            "duracion_total_minutos": duracion_total_minutos,
            "cantidad_servicios": len(servicios)
        }

class CitaService:
    """Reglas de negocio de las citas (horarios, choques, creación)."""

    # Estados en los que la cita OCUPA el turno del especialista.
    ESTADOS_QUE_OCUPAN_AGENDA = ('PENDIENTE', 'CONFIRMADA', 'PAGO COMPLETO', 'COMPLETADA')

    @staticmethod
    def _nombre_profesional(trabajador: PerfilUsuario) -> str:
        """Nombre legible del profesional (PerfilUsuario no tiene campo `nombre`)."""
        usuario = trabajador.usuariof
        return usuario.get_full_name() or usuario.username

    @staticmethod
    def validar_horario_establecimiento(establecimiento, fecha_cita, hora_inicio, duracion: int) -> bool:
        """Reglas del SALÓN: medianoche, día cerrado y horario de atención."""
        inicio_dt = FechaCita.obtenerElTiempoDeLaFecha(fecha_cita, hora_inicio)
        fin_dt = inicio_dt + timedelta(minutes=duracion)
        hora_fin = fin_dt.time()

        if fin_dt.date() > fecha_cita:
            raise ValidationError("La cita no puede terminar después de la medianoche.")

        horario_salon = HorarioEstablecimiento.objects.filter(
            establecimientof=establecimiento,
            dia_semana=fecha_cita.isoweekday()   # 1 = lunes ... 7 = domingo
        ).first()
        if horario_salon:
            if horario_salon.cerrado:
                raise ValidationError("El establecimiento permanece cerrado el día seleccionado.")
            if horario_salon.hora_apertura and horario_salon.hora_cierre:
                if hora_inicio < horario_salon.hora_apertura or hora_fin > horario_salon.hora_cierre:
                    raise ValidationError(
                        "El horario seleccionado está fuera del horario de atención del establecimiento."
                    )
        return True

    # ------------------------------------------------------------------
    # RN-03: CHOQUES DE CITAS
    # ------------------------------------------------------------------
    @staticmethod
    def _cita_que_choca(citas, fecha_cita, hora_inicio, duracion: int):
        """
        Recibe citas del MISMO día y devuelve la primera que se pise con el
        rango pedido (o None si ninguna choca).

        Dos rangos se pisan si CADA UNO empieza antes de que el otro termine.
        10:00-11:00 y 11:00-12:00 NO chocan (una termina cuando empieza la otra).
        Se calcula en Python porque `hora_fin` es una property, no una columna.
        """
        ahora = timezone.now()
        nueva_inicio = datetime.combine(fecha_cita, hora_inicio)
        nueva_fin = nueva_inicio + timedelta(minutes=duracion)

        for otra in citas:
            # RN-05: una cita pendiente con el plazo de pago vencido ya no ocupa el turno.
            if otra.estado == 'PENDIENTE' and otra.fecha_expiracion and otra.fecha_expiracion < ahora:
                continue

            # La cita guarda solo la hora de inicio; su duración es la suma de sus servicios.
            minutos_otra = sum(srv.duracion_minutos for srv in otra.serviciof.all())
            otra_inicio = datetime.combine(fecha_cita, otra.hora_inicio)
            otra_fin = otra_inicio + timedelta(minutes=minutos_otra)

            if otra_inicio < nueva_fin and otra_fin > nueva_inicio:
                return otra
        return None

    @staticmethod
    def validar_choque_trabajador(
            trabajador: PerfilUsuario,
            fecha_cita,
            hora_inicio,
            duracion: int,
            cita_id_actual=None) -> bool:
        """
        RN-03 (especialista): no puede tener dos citas en la misma franja.
        `cita_id_actual` = cita que se está EDITANDO (para no compararla consigo misma).
        """
        if not trabajador or not fecha_cita or not hora_inicio:
            return True

        citas_del_dia = Cita.objects.filter(
            trabajadorf=trabajador,
            fecha_cita=fecha_cita,
            estado__in=CitaService.ESTADOS_QUE_OCUPAN_AGENDA,
            estadocita=True,
        ).prefetch_related('serviciof')
        if cita_id_actual:
            citas_del_dia = citas_del_dia.exclude(pk=cita_id_actual)

        if CitaService._cita_que_choca(citas_del_dia, fecha_cita, hora_inicio, duracion):
            fin = (datetime.combine(fecha_cita, hora_inicio) + timedelta(minutes=duracion)).time()
            raise ValidationError(
                f"El profesional {CitaService._nombre_profesional(trabajador)} no tiene disponibilidad "
                f"en el rango horario seleccionado ({hora_inicio.strftime('%H:%M')} - {fin.strftime('%H:%M')})."
            )
        return True

    @staticmethod
    def validar_choque_cliente(
            correo_cliente: str,
            fecha_cita,
            hora_inicio,
            duracion: int,
            cita_id_actual=None) -> bool:
        """
        RN-03 (cliente): la misma persona (mismo correo) no puede tener dos
        citas cruzadas. Se compara en todos los salones.
        """
        if not correo_cliente or not fecha_cita or not hora_inicio:
            return True

        citas_del_dia = Cita.objects.filter(
            correo_cliente__iexact=correo_cliente.strip(),   # iexact = ignora mayúsculas
            fecha_cita=fecha_cita,
            estado__in=CitaService.ESTADOS_QUE_OCUPAN_AGENDA,
            estadocita=True,
        ).prefetch_related('serviciof')
        if cita_id_actual:
            citas_del_dia = citas_del_dia.exclude(pk=cita_id_actual)

        if CitaService._cita_que_choca(citas_del_dia, fecha_cita, hora_inicio, duracion):
            fin = (datetime.combine(fecha_cita, hora_inicio) + timedelta(minutes=duracion)).time()
            raise ValidationError(
                f"El cliente ya tiene otra cita que se cruza con este horario "
                f"({hora_inicio.strftime('%H:%M')} - {fin.strftime('%H:%M')})."
            )
        return True

    # ------------------------------------------------------------------
    @staticmethod
    def validar_horario(
            trabajador: PerfilUsuario,
            fecha_cita,
            hora_inicio,
            duracion: int,
            cita_id_actual=None) -> bool:
        """
        Comprueba que el horario sea posible para el especialista:
        salón abierto, turno del trabajador, descanso y choque con otras citas.
        """
        if not trabajador or not fecha_cita or not hora_inicio:
            return True

        dia_semana_num = fecha_cita.isoweekday()

        inicio_dt = FechaCita.obtenerElTiempoDeLaFecha(fecha_cita, hora_inicio)
        fin_dt = inicio_dt + timedelta(minutes=duracion)
        hora_fin = fin_dt.time()

        # 1. Horario del salón
        CitaService.validar_horario_establecimiento(
            trabajador.establecimientof, fecha_cita, hora_inicio, duracion
        )

        # 2. Turno del especialista
        horario = HorarioTrabajador.objects.filter(
            trabajadorf=trabajador,
            dia_semana=dia_semana_num,
            activo=True
        ).first()
        if not horario:
            raise ValidationError(
                "El profesional no labora o se encuentra inactivo el día seleccionado."
            )

        if hora_inicio < horario.hora_entrada or hora_fin > horario.hora_salida:
            raise ValidationError("El horario seleccionado está fuera de las horas de trabajo del profesional.")

        # 3. Descanso
        if horario.descanso_inicio and horario.descanso_fin:
            if hora_inicio < horario.descanso_fin and hora_fin > horario.descanso_inicio:
                raise ValidationError("El horario seleccionado interfiere con la franja de descanso del profesional.")

        # 4. Choque con otras citas del especialista (RN-03)
        CitaService.validar_choque_trabajador(
            trabajador, fecha_cita, hora_inicio, duracion, cita_id_actual
        )

        return True

    @staticmethod
    def trabajador_disponible(trabajador: PerfilUsuario, fecha_cita, hora_inicio, duracion: int) -> bool:
        """¿Puede este profesional atender `duracion` minutos a esa hora? (sí/no, sin lanzar error)."""
        try:
            CitaService.validar_horario(
                trabajador=trabajador,
                fecha_cita=fecha_cita,
                hora_inicio=hora_inicio,
                duracion=duracion
            )
        except ValidationError:
            return False
        return True

    @staticmethod
    def secuencia_disponible(trabajador: PerfilUsuario, servicios: List[Servicio], fecha_cita, hora_inicio) -> bool:
        """¿Puede hacer TODOS los servicios seguidos, uno tras otro?"""
        hora_bloque = hora_inicio
        for srv in servicios:
            if not CitaService.trabajador_disponible(trabajador, fecha_cita, hora_bloque, srv.duracion_minutos):
                return False
            hora_bloque = FechaCita.sumarMinutos(fecha_cita, hora_bloque, srv.duracion_minutos)
        return True

    @staticmethod
    @transaction.atomic
    def validarCitaPendiente(
        servicios: Union[Servicio, List[Servicio], QuerySet],
        establecimiento: Establecimiento,
        trabajador: PerfilUsuario = None,  # Opcional si el cliente lo elige
        fecha_cita=None,
        hora_inicio=None,
        nombre_cliente: str = "",
        correo: str = "",
        telefono: str = "",
        notas: str = None
    ) -> Cita:
        """
        Crea una cita PENDIENTE (7 minutos para pagar el anticipo del 30%).
        @transaction.atomic: si algo falla, no se guarda nada a medias.
        """
        if isinstance(servicios, Servicio):
            lista_servicios = [servicios]
        else:
            lista_servicios = list(servicios)

        if not lista_servicios:
            raise ValidationError("Debe seleccionar al menos un servicio.")
        if not fecha_cita or not hora_inicio:
            raise ValidationError("Debe indicar la fecha y la hora de la cita.")

        # RN-08 / RN-11: salón, servicios y trabajador activos y del mismo salón.
        ValidarService.validar_multicliente(
            servicios=lista_servicios,
            establecimiento=establecimiento,
            trabajador=trabajador
        )

        # RN-01: anticipación mínima.
        FechaCita.anticipacionMinima(fecha_cita=fecha_cita, hora_inicio=hora_inicio, anticipacion=3)

        # Reglas del salón para todo el bloque.
        duracion_total = sum(srv.duracion_minutos for srv in lista_servicios)
        CitaService.validar_horario_establecimiento(establecimiento, fecha_cita, hora_inicio, duracion_total)

        # RN-03 (cliente): la misma persona no puede tener dos citas cruzadas.   <-- NUEVO
        CitaService.validar_choque_cliente(correo, fecha_cita, hora_inicio, duracion_total)

        # RNF-05: bloqueo para que dos clientes no tomen el mismo turno a la vez.
        list(PerfilUsuario.objects.select_for_update().filter(
            establecimientof=establecimiento,
            rol=PerfilUsuario.RolChoices.TRABAJADOR,
            estado=True,
        ).order_by('pk'))

        # RN-06 / RN-07: quién atiende cada servicio (el primero DISPONIBLE).
        asignaciones = ValidarService.validar_trabajadores(
            servicios=lista_servicios,
            establecimiento=establecimiento,
            trabajador=trabajador,
            fecha_cita=fecha_cita,
            hora_inicio=hora_inicio
        )

        # RN-03 (especialista): confirmación final bloque por bloque.
        hora_actual_bloque = hora_inicio
        for item in asignaciones:
            srv = item['servicio']
            profesional = item['trabajador']

            CitaService.validar_horario(
                trabajador=profesional,
                fecha_cita=fecha_cita,
                hora_inicio=hora_actual_bloque,
                duracion=srv.duracion_minutos
            )

            hora_actual_bloque = FechaCita.sumarMinutos(fecha_cita, hora_actual_bloque, srv.duracion_minutos)

        # RN-05: crear la cita con 7 minutos para pagar.
        fecha_expiracion = timezone.now() + timedelta(minutes=7)

        cita = Cita.objects.create(
            nombre_cliente=nombre_cliente,
            correo_cliente=correo,
            telefono_cliente=telefono,
            fecha_cita=fecha_cita,
            hora_inicio=hora_inicio,
            estado='PENDIENTE',
            fecha_expiracion=fecha_expiracion,
            nota=notas,
            nombre_establecimiento=establecimiento.nombre,
        )

        cita.serviciof.set(lista_servicios)
        trabajadores_unicos = list({item['trabajador'] for item in asignaciones})
        cita.trabajadorf.set(trabajadores_unicos)

        return cita

    @staticmethod
    def validarToleranciaDeRetraso(cita: Cita) -> bool:
        """RN-02: pasados 15 minutos de la hora pactada, la cita puede marcarse como inasistencia."""
        if cita.estado not in ['PENDIENTE', 'CONFIRMADA']:
            raise ValidationError(
                f"La cita se encuentra en estado '{cita.estado}' y no puede evaluarse por inasistencia."
            )

        dt_cita = FechaCita.obtenerElTiempoDeLaFecha(cita.fecha_cita, cita.hora_inicio)
        ahora = timezone.now()

        limite_tolerancia = dt_cita + timedelta(minutes=15)

        if ahora < limite_tolerancia:
            minutos_restantes = int((limite_tolerancia - ahora).total_seconds() / 60)
            raise ValidationError(
                f"Aún no han transcurrido los 15 minutos de tolerancia para la cita #{cita.pk}. "
                f"Faltan {minutos_restantes} minuto(s)."
            )

        return True
class FechaCita:
    @staticmethod
    def obtenerElTiempoDeLaFecha(fecha_cita, hora_inicio) -> datetime:
        fecha_hora = datetime.combine(fecha_cita, hora_inicio)
        if timezone.is_naive(fecha_hora):
            return timezone.make_aware(fecha_hora)
        return fecha_hora

    @staticmethod
    def sumarMinutos(fecha_cita, hora, minutos: int):
        """Devuelve la hora que resulta de sumarle `minutos` a `hora` (ej: 10:00 + 45 min = 10:45)."""
        inicio_dt = FechaCita.obtenerElTiempoDeLaFecha(fecha_cita, hora)
        return (inicio_dt + timedelta(minutes=minutos)).time()

    @staticmethod
    def validarHorasFaltantes(fecha_cita, hora_inicio) -> float:
        dt_inicio = FechaCita.obtenerElTiempoDeLaFecha(fecha_cita, hora_inicio)
        ahora = timezone.now()
        faltante = dt_inicio - ahora
        return faltante.total_seconds() / 3600

    @staticmethod
    def anticipacionMinima(fecha_cita, hora_inicio, anticipacion: int = 3):
        horasAnticipadas = FechaCita.validarHorasFaltantes(fecha_cita, hora_inicio)
        horasRequeridas = anticipacion * 24

        if horasAnticipadas < horasRequeridas:
            raise ValidationError(f"Se requiere una anticipación de al menos {anticipacion} días para agendar.")
        return True

    @staticmethod
    def fechaMinimaParaCancelar(fecha_cita, hora_inicio, hora_limite: int = 24) -> bool:

        fechaCancelar = FechaCita.validarHorasFaltantes(fecha_cita, hora_inicio)
        return fechaCancelar > hora_limite

class EstablecimientoService:
 
    @staticmethod
    @transaction.atomic
    def inactivar_establecimiento_en_cascada(establecimiento: Establecimiento):
        establecimiento.estado = False
        establecimiento.save()

        Categoria.objects.filter(establecimientof=establecimiento).update(estado=False)
        Servicio.objects.filter(categoriaf__establecimientof=establecimiento).update(estado=False)
        PerfilUsuario.objects.filter(establecimientof=establecimiento).update(estado=False)
        HorarioTrabajador.objects.filter(trabajadorf__establecimientof=establecimiento).update(activo=False)

        Cita.objects.filter(serviciof__categoriaf__establecimientof=establecimiento).update(estadocita=False)
        Resena.objects.filter(citaf__serviciof__categoriaf__establecimientof=establecimiento).update(estado=False)
        Factura.objects.filter(citaf__serviciof__categoriaf__establecimientof=establecimiento).update(estado=False)
        FacturaDetalle.objects.filter(facturaf__citaf__serviciof__categoriaf__establecimientof=establecimiento).update(estado=False)

    @staticmethod
    @transaction.atomic
    def activar_establecimientos(establecimiento: Establecimiento):
        # Es lo contrario: se reactiva el salón y todos sus registros.
        establecimiento.estado = True
        establecimiento.save()

        Categoria.objects.filter(establecimientof=establecimiento).update(estado=True)
        Servicio.objects.filter(categoriaf__establecimientof=establecimiento).update(estado=True)
        PerfilUsuario.objects.filter(establecimientof=establecimiento).update(estado=True)
        HorarioTrabajador.objects.filter(trabajadorf__establecimientof=establecimiento).update(activo=True)

        Cita.objects.filter(serviciof__categoriaf__establecimientof=establecimiento).update(estadocita=True)
        Resena.objects.filter(citaf__serviciof__categoriaf__establecimientof=establecimiento).update(estado=True)
        Factura.objects.filter(citaf__serviciof__categoriaf__establecimientof=establecimiento).update(estado=True)
        FacturaDetalle.objects.filter(facturaf__citaf__serviciof__categoriaf__establecimientof=establecimiento).update(estado=True)

class ResenaService:

    @staticmethod
    def validar_y_crear_resena(
        cita: Cita, 
        calificacion: int, 
        comentario: str
    ) -> Resena:
        """Validar que la reseña pertenezca a una cita COMPLETADA.
        El cliente no tiene cuenta: la reseña queda ligada a su cita.
        """
        if cita.estado != 'COMPLETADA':
            raise ValidationError(
                "Solo se pueden publicar reseñas para citas que hayan sido completadas."
            )

        if Resena.objects.filter(citaf=cita).exists():
            raise ValidationError(
                "Esta cita ya cuenta con una reseña registrada."
            )
        resena = Resena.objects.create(
            citaf=cita,
            nombre_establecimiento=cita.nombre_establecimiento,
            calificacion=calificacion,
            comentario=comentario
        )
        return resena
 
class PermisosService:
 
    @staticmethod
    def validar_acceso_interno(usuario: User, establecimiento: Establecimiento):

        # El Superadmin puede ver cualquier salón.
        if usuario.is_superuser or obtener_rol(usuario) == Rol.SUPERADMIN:
            return True
 
        if not establecimiento.estado:
            raise ValidationError("El establecimiento se encuentra suspendido por falta de pago.")
 
        rol = obtener_rol(usuario)
        if rol is None:   # cuenta, perfil o salón inactivos
            raise PermissionDenied("Su cuenta, perfil o establecimiento se encuentra inactivo.")

        propio = obtener_establecimiento(usuario)
        if rol not in PerfilUsuario.ROLES_CON_ESTABLECIMIENTO or propio is None or propio.pk != establecimiento.pk:
            raise PermissionDenied("No tiene permisos sobre los datos de este establecimiento.")

        return True

class CitaQueryService:

    @staticmethod
    def obtener_citas_panel(usuario: User):

        if not getattr(usuario, 'is_authenticated', False):
            raise PermissionDenied("Acceso restringido a usuarios registrados del sistema.")
 
        rol = obtener_rol(usuario)
        if rol is None:
            perfil = obtener_perfil(usuario)
            if perfil is not None and perfil.establecimientof and not perfil.establecimientof.estado:
                raise PermissionDenied(
                    "Acceso denegado: El establecimiento se encuentra inactivo por falta de pago.")
            raise PermissionDenied("Su cuenta o perfil se encuentra inactivo o sin rol asignado.")

        if rol not in (Rol.SUPERADMIN, Rol.ADMIN_NEGOCIO, Rol.ASISTENTE, Rol.TRABAJADOR):
            raise PermissionDenied("Rol no autorizado para consultar el panel de citas.")

        return filtrar_query_por_user(Cita.objects.all(), usuario)

class ComisionServices:
    @staticmethod
    def calcularLaComisiones(
        trabajador: PerfilUsuario,
        estados: Union[str, List[str]] = 'COMPLETADA',
        fecha_inicio=None,
        fecha_fin=None
    ) -> dict:

        if isinstance(estados, str):
            lista_estados = [estados]
        else:
            lista_estados = list(estados)

        citas = Cita.objects.filter(
            trabajadorf=trabajador,
            estado__in=lista_estados,
            estadocita=True,
        ).prefetch_related('serviciof')

        if fecha_inicio:
            citas = citas.filter(fecha_cita__gte=fecha_inicio)
        if fecha_fin:
            citas = citas.filter(fecha_cita__lte=fecha_fin)

        ahora = timezone.now()
        monto_total_generado = Decimal('0.00')
        citas_validas = []

        for cita in citas:
            dt_cita = FechaCita.obtenerElTiempoDeLaFecha(cita.fecha_cita, cita.hora_inicio)

            if dt_cita <= ahora:
                citas_validas.append(cita)
                for servicio in cita.serviciof.all():
                    monto_total_generado += Decimal(str(servicio.precio))

        porcentaje = trabajador.porcentaje_comision
        monto_comision = (monto_total_generado * (porcentaje / Decimal('100.00'))).quantize(Decimal('0.01'))

        usuario = trabajador.usuariof 

        return {
            "trabajador_uuid": trabajador.codigo_unico,
            "nombre_trabajador": usuario.get_full_name() or usuario.username,
            "porcentaje_comision": porcentaje,
            "estados_consultados": lista_estados,
            "monto_total_generado": monto_total_generado,
            "monto_comision": monto_comision,
            "total_citas": len(citas_validas),
            "citas": citas_validas  # solo las citas cuya hora ya pasó
        }