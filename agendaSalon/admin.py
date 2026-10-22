from django import forms
from django.contrib import admin, messages
# Formulario de login que trae Django para el panel; lo ampliamos más abajo.
from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.auth import password_validation
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied, ValidationError
from django.utils.translation import gettext_lazy as _   # marca textos "traducibles"
from .services import EstablecimientoService
 
from .models import (
    Establecimiento,
    PerfilUsuario,
    Categoria,
    Servicio,
    Cita,
    Factura,
    FacturaDetalle,
    #Resena,
    HorarioEstablecimiento,
    HorarioTrabajador,
)
# Todo lo que importamos de permissions.py: las REGLAS que aquí solo se aplican.
from .permissions import (
    Rol,
    VER,
    AGREGAR,
    CAMBIAR,
    ELIMINAR,
    MODELOS_CON_ESTABLECIMIENTO,
    acceso_admin,
    es_superadmin,
    filtrar_query_por_user,
    obtener_establecimiento,
    obtener_perfil,
    puede_acceder_objeto,
    roles_asignables,
    tiene_algun_permiso,
    tiene_permiso,
    tiene_permiso_especial,
)
from .services import (
    EstablecimientoService,
    CitaService,
    FechaCita,
    ServicioService,
)

ROLES_QUE_ATIENDEN = [Rol.TRABAJADOR,]

class SalonAdminAuthenticationForm(AdminAuthenticationForm):
    """
    Formulario de login del panel con una revisión extra: aunque la contraseña
    sea correcta, NO deja entrar si el perfil o el salón están inactivos
    (RN-08 y RN-11), o si el rol no tiene acceso al panel (Cliente).
    """
 
    def confirm_login_allowed(self, user):
        # Primero las comprobaciones normales de Django (cuenta activa y staff).
        super().confirm_login_allowed(user)
        # Después, la nuestra (definida en permissions.py).
        if not acceso_admin(user):
            raise ValidationError(
                _('Su perfil o el establecimiento al que pertenece se encuentra inactivo, '
                  'o su rol no tiene acceso al panel.'),
                code='invalid_login',
            )

admin.site.login_form = SalonAdminAuthenticationForm
admin.site.site_header = _('Gestión de Salones de Belleza')
admin.site.site_title = _('Salones')
admin.site.index_title = _('Panel de administración')

_has_permission_original = admin.site.has_permission

def _has_permission_salon(request):
    return _has_permission_original(request) and acceso_admin(request.user)

admin.site.has_permission = _has_permission_salon

class CategoriaListFilter(admin.SimpleListFilter):

    title = _('Categoría')
    parameter_name = 'categoria_id'   
 
    def lookups(self, request, model_admin):
        # Opciones del filtro: ya recortadas al salón del usuario.
        categorias = filtrar_query_por_user(Categoria.objects.all(), request.user)
        return [(cat.pk, cat.nombre) for cat in categorias]
 
    def queryset(self, request, queryset):
        categoria_id = self.value()   # lo que el usuario eligió (o None)
        if not categoria_id:
            return queryset           # no eligió nada: no se filtra
        model = queryset.model
        if model == Categoria:
            return queryset.filter(pk=categoria_id)
        # Servicio tiene el campo `categoriaf` directamente.
        if hasattr(model, 'categoriaf'):
            return queryset.filter(categoriaf_id=categoria_id)
        # Cita llega a la categoría pasando por sus servicios (varios por cita).
        if hasattr(model, 'serviciof'):
            return queryset.filter(pk__in=model.objects.filter(
                serviciof__categoriaf_id=categoria_id).values('pk'))
        return queryset

class SalonAdminMixin:
    empty_value_display = _('- Sin información -')   # texto cuando un campo está vacío
    # Campos que solo el SUPERADMIN puede editar (para los demás: solo lectura).
    readonly_para_no_superadmin = ()
 
    @property
    def _modelo(self):
        """Nombre del modelo en minúscula (ej: 'cita'), la clave de la matriz."""
        return self.model._meta.model_name
 

    def has_module_permission(self, request):
        """¿Aparece este modelo en el menú del panel? Sí, si tiene algún permiso sobre él."""
        return tiene_algun_permiso(request.user, self._modelo)
 
    def has_view_permission(self, request, obj=None):
        """
        ¿Puede VER? `obj` es None cuando pide la lista, y un registro concreto
        cuando abre uno. En ese caso también comprobamos que sea de su salón.
        Quien puede CAMBIAR también puede ver.
        """
        if not (tiene_permiso(request.user, self._modelo, VER)
                or tiene_permiso(request.user, self._modelo, CAMBIAR)):
            return False
        return obj is None or puede_acceder_objeto(request.user, obj)
 
    def has_add_permission(self, request):
        """¿Aparece el botón 'Añadir'?"""
        return tiene_permiso(request.user, self._modelo, AGREGAR)
 
    def has_change_permission(self, request, obj=None):
        """¿Puede EDITAR (ese registro, si se indica)?"""
        if not tiene_permiso(request.user, self._modelo, CAMBIAR):
            return False
        return obj is None or puede_acceder_objeto(request.user, obj)
 
    def has_delete_permission(self, request, obj=None):
        """¿Puede BORRAR? (casi nadie: los registros se inactivan, no se borran)."""
        if not tiene_permiso(request.user, self._modelo, ELIMINAR):
            return False
        return obj is None or puede_acceder_objeto(request.user, obj)
 
    # ---- AISLAMIENTO MULTI-TENANT --------------------------------------------
    def get_queryset(self, request):
        """
        Lista que se muestra en el panel. `super().get_queryset(request)` es la
        lista completa; la pasamos por filtrar_query_por_user para que
        cada usuario reciba SOLO lo suyo (RNF-04).
        """
        return filtrar_query_por_user(super().get_queryset(request), request.user)
 
    @staticmethod
    def _trabajadores_que_atienden(request, queryset=None):
        """Trabajadores activos del salón del usuario (para los desplegables)."""
        qs = queryset if queryset is not None else PerfilUsuario.objects.all()
        qs = filtrar_query_por_user(qs, request.user)
        return qs.filter(rol__in=ROLES_QUE_ATIENDEN, estado=True)
 
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Recorta los DESPLEGABLES (relaciones "uno a muchos"). Sin esto, al crear
        un servicio, el Admin del salón A vería en el desplegable las categorías
        del salón B aunque después no pudiera guardarlas.
        """
        related = db_field.remote_field.model   # modelo al que apunta el campo
        if related is PerfilUsuario and db_field.name == 'trabajadorf':
            kwargs['queryset'] = self._trabajadores_que_atienden(request, kwargs.get('queryset'))
        elif related in MODELOS_CON_ESTABLECIMIENTO and not es_superadmin(request.user):
            qs = kwargs.get('queryset', related.objects.all())
            kwargs['queryset'] = filtrar_query_por_user(qs, request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
 
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """Lo mismo, pero para relaciones "muchos a muchos" (ej: servicios de una cita)."""
        related = db_field.remote_field.model
        if related is PerfilUsuario:
            kwargs['queryset'] = self._trabajadores_que_atienden(request, kwargs.get('queryset'))
        elif related in MODELOS_CON_ESTABLECIMIENTO and not es_superadmin(request.user):
            qs = kwargs.get('queryset', related._default_manager.all())
            kwargs['queryset'] = filtrar_query_por_user(qs, request.user)
        return super().formfield_for_manytomany(db_field, request, **kwargs)
 
    def get_form(self, request, obj=None, **kwargs):
        """Si el formulario tiene el campo 'establecimientof', lo deja fijo en el salón del usuario."""
        form = super().get_form(request, obj, **kwargs)
        est = obtener_establecimiento(request.user)
        campo = form.base_fields.get('establecimientof')
        if campo is not None and est is not None and not es_superadmin(request.user):
            campo.initial = est.pk       # viene preseleccionado
            campo.empty_label = None     # y no se puede dejar vacío
        return form
 
    def get_readonly_fields(self, request, obj=None):
        """Campos de solo lectura: los del ModelAdmin + los reservados al Superadmin."""
        readonly = list(super().get_readonly_fields(request, obj))
        if not es_superadmin(request.user):
            readonly += [f for f in self.readonly_para_no_superadmin if f not in readonly]
        return readonly
 
 

# 4. UN ModelAdmin POR MODELO

# @admin.register(Modelo) = "muestra este modelo en el panel con esta configuración".
# Todos heredan de SalonAdminMixin para aplicar las reglas de permissions.py.

# ESTABLECIMIENTO  (Superadmin: alta/baja | Admin: edita los datos de SU local)

@admin.register(Establecimiento)
class EstablecimientoAdmin(SalonAdminMixin, admin.ModelAdmin):
    list_display = ('nombre', 'nit', 'telefono', 'correo', 'ciudad', 'estado')   # columnas de la lista
    search_fields = ('nombre', 'nit', 'correo', 'telefono', 'codigo_unico')       # buscador
    list_filter = ('estado', 'ciudad')                                            # filtros laterales
    # `estado` es de solo lectura A PROPÓSITO: no se cambia con la casilla, sino
    # con las acciones de abajo, para que la inactivación en cascada 
    readonly_fields = ('estado', 'slug', 'codigo_unico', 'creado_en')
    # Datos legales/identidad: solo el Superadmin los puede cambiar.
    readonly_para_no_superadmin = ('nit', 'razon_social', 'nombre')
    actions = ['activar_establecimientos', 'desactivar_establecimientos']

    def has_gestionar_ciclo_vida_permission(self, request):

        return tiene_permiso_especial(request.user, 'gestionar_ciclo_de_establecimiento')

    @admin.action(description=_('Activar establecimientos seleccionados'),
                  permissions=['gestionar_ciclo_vida'])
    def activar_establecimientos(self, request, queryset):
        total = 0
        for establecimiento in queryset:
            EstablecimientoService.activar_establecimientos(establecimiento)
            total += 1
        self.message_user(
            request,
            _('%(count)d establecimiento(s) activado(s) exitosamente.') % {'count': total},
            messages.SUCCESS,
        )

    @admin.action(description=_('Desactivar establecimientos seleccionados'),
                  permissions=['gestionar_ciclo_vida'])
    def desactivar_establecimientos(self, request, queryset):
        total = 0
        for establecimiento in queryset:
            EstablecimientoService.inactivar_establecimiento_en_cascada(establecimiento)
            total += 1
        self.message_user(
            request,
            _('%(count)d establecimiento(s) desactivado(s) con todos sus registros (RN-11).') % {'count': total},
            messages.WARNING,
        )

# PERFIL DE USUARIO / PERSONAL

class PerfilUsuarioCreacionForm(forms.ModelForm):

    # Campos del User de Django (no existen en PerfilUsuario, por eso se declaran aquí).
    username = forms.CharField(max_length=150, label=_('Usuario'))
    email = forms.EmailField(label=_('Correo electrónico'))
    first_name = forms.CharField(max_length=150, label=_('Nombres'))
    last_name = forms.CharField(max_length=150, required=False, label=_('Apellidos'))
    # widget=PasswordInput -> muestra puntos en vez de letras al escribir.
    password1 = forms.CharField(label=_('Contraseña'), strip=False, widget=forms.PasswordInput)
    password2 = forms.CharField(label=_('Confirmar contraseña'), strip=False, widget=forms.PasswordInput)

    class Meta:
        model = PerfilUsuario
        fields = ('rol', 'establecimientof', 'telefono', 'porcentaje_comision', 'imagen', 'estado')

    # Los métodos clean_<campo> validan UN campo. Si lanzan ValidationError,
    # el formulario muestra el mensaje junto a ese campo.
    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username__iexact=username).exists():   # iexact = sin importar mayúsculas
            raise ValidationError(_("El nombre de usuario '%(u)s' ya está registrado."), params={'u': username})
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError(_("El correo '%(e)s' ya se encuentra en uso."), params={'e': email})
        return email

    def clean(self):
        """Validación que cruza varios campos: las dos contraseñas deben coincidir y ser seguras."""
        cleaned = super().clean()
        p1, p2 = cleaned.get('password1'), cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            self.add_error('password2', _('Las contraseñas no coinciden.'))
        elif p1:
            # Se crea un User "de prueba" (sin guardarlo) para que el validador pueda
            # rechazar contraseñas parecidas al usuario o al correo (RNF-03).
            candidato = User(
                username=cleaned.get('username', ''),
                email=cleaned.get('email', ''),
                first_name=cleaned.get('first_name', ''),
                last_name=cleaned.get('last_name', ''),
            )
            try:
                password_validation.validate_password(p1, candidato)
            except ValidationError as err:
                self.add_error('password1', err)
        return cleaned

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(SalonAdminMixin, admin.ModelAdmin):
    list_display = ('nombre_completo', 'usuario', 'rol', 'nombre_establecimiento', 'estado')
    list_filter = ('rol', 'estado')
    search_fields = ('usuariof__username', 'usuariof__first_name', 'usuariof__last_name',
                     'usuariof__email', 'nombre_establecimiento', 'codigo_unico')
    # Trae el usuario y el salón en la MISMA consulta SQL (más rápido que una por fila).
    list_select_related = ('usuariof', 'establecimientof')
    fieldsets_creacion = (
        (_('Cuenta de acceso'), {'fields': ('username', 'email', 'first_name', 'last_name',
                                            'password1', 'password2')}),
        (_('Perfil'), {'fields': ('rol', 'establecimientof', 'telefono', 'porcentaje_comision',
                                  'imagen', 'estado')}),
    )
    fieldsets_edicion = (
        (_('Cuenta de acceso'), {'fields': ('usuariof',)}),
        (_('Perfil'), {'fields': ('rol', 'establecimientof', 'nombre_establecimiento', 'telefono',
                                  'porcentaje_comision', 'imagen', 'estado', 'codigo_unico')}),
    )

    @admin.display(description=_('Nombre'))
    def nombre_completo(self, obj):
        return obj.usuariof.get_full_name() or obj.usuariof.username

    @admin.display(description=_('Usuario'), ordering='usuariof__username')
    def usuario(self, obj):
        return obj.usuariof.username

    def get_fieldsets(self, request, obj=None):
        # obj es None cuando se está CREANDO uno nuevo.
        return self.fieldsets_creacion if obj is None else self.fieldsets_edicion

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            kwargs['form'] = PerfilUsuarioCreacionForm   # al crear, usa el formulario especial
        form = super().get_form(request, obj, **kwargs)
        # Muestra solo los roles que ESTE usuario puede asignar (evita que un
        # Admin de salón se cree un Superadmin: "escalada de privilegios").
        campo_rol = form.base_fields.get('rol')
        if campo_rol is not None:
            permitidos = {str(r) for r in roles_asignables(request.user)}
            campo_rol.choices = [(v, l) for v, l in campo_rol.choices if v in permitidos or v == '']
        return form

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return ['nombre_establecimiento', 'codigo_unico']
        readonly = ['usuariof', 'nombre_establecimiento', 'codigo_unico']
        if not es_superadmin(request.user):
            readonly.append('establecimientof')   # el personal no se cambia de salón
        propio = obtener_perfil(request.user)
        # Nadie puede cambiarse a sí mismo el rol ni desactivarse; y tampoco se
        # editan los roles que uno no tiene permiso de asignar.
        if (propio is not None and obj.pk == propio.pk) or obj.rol not in {str(r) for r in roles_asignables(request.user)}:
            readonly += ['rol', 'estado']
        return readonly

    def has_change_permission(self, request, obj=None):
        if not super().has_change_permission(request, obj):
            return False
        if obj is not None and not es_superadmin(request.user):
            propio = obtener_perfil(request.user)
            # Un Admin de salón no puede editar a OTRO Admin (solo a sí mismo).
            if obj.rol == Rol.ADMIN_NEGOCIO and (propio is None or obj.pk != propio.pk):
                return False
        return True

    def save_model(self, request, obj, form, change):
        usuario = request.user
        # Un Admin/Asistente siempre crea personal EN SU salón, sin importar lo que envíe.
        if not es_superadmin(usuario):
            obj.establecimientof = obtener_establecimiento(usuario)
        # Verifica otra vez que el rol asignado sea uno permitido.
        if obj.rol not in {str(r) for r in roles_asignables(usuario)} and not (
                change and obj.rol == PerfilUsuario.objects.get(pk=obj.pk).rol):
            raise PermissionDenied('No puede asignar ese rol.')
        if not change:
            # Registro nuevo: primero se crea el User de Django. create_user
            # guarda la contraseña ENCRIPTADA.
            cd = form.cleaned_data
            obj.usuariof = User.objects.create_user(
                username=cd['username'],
                email=cd['email'],
                password=cd['password1'],
                first_name=cd['first_name'],
                last_name=cd.get('last_name', ''),
            )
        super().save_model(request, obj, form, change)

# CATÁLOGO: CATEGORÍAS Y SERVICIOS

@admin.register(Categoria)
class CategoriaAdmin(SalonAdminMixin, admin.ModelAdmin):
    list_display = ('nombre', 'nombre_establecimiento', 'estado')
    list_filter = ('estado',)
    search_fields = ('nombre',)
    readonly_fields = ('nombre_establecimiento',)

@admin.register(Servicio)
class ServicioAdmin(SalonAdminMixin, admin.ModelAdmin):
    list_display = ('nombre', 'categoriaf', 'precio_formateado', 'duracion_minutos', 'estado')
    list_filter = (CategoriaListFilter, 'estado')
    search_fields = ('nombre', 'codigo_unico')
    readonly_fields = ('nombre_establecimiento', 'codigo_unico')
    filter_horizontal = ('trabajadoresf',)
    list_select_related = ('categoriaf',)

# HORARIOS
@admin.register(HorarioEstablecimiento)
class HorarioEstablecimientoAdmin(SalonAdminMixin, admin.ModelAdmin):
    # `cerrado` = el salón no abre ese día 
    # horas de apertura y cierre pueden quedar vacías.
    list_display = ('establecimientof', 'dia_semana', 'hora_apertura', 'hora_cierre', 'cerrado')
    list_filter = ('dia_semana', 'cerrado')

@admin.register(HorarioTrabajador)
class HorarioTrabajadorAdmin(SalonAdminMixin, admin.ModelAdmin):
    list_display = ('trabajadorf', 'dia_semana', 'hora_entrada', 'hora_salida', 'activo')
    list_filter = ('dia_semana', 'activo')
    list_select_related = ('trabajadorf__usuariof',)

# CITAS

class CitaAdminForm(forms.ModelForm):
    """
    Formulario de citas con reglas de negocio. Se usa cuando la recepción
    registra una cita a mano.
    """

    class Meta:
        model = Cita
        fields = '__all__'

    def clean(self):
        cleaned = super().clean()
        servicios = cleaned.get('serviciof')
        trabajadores = cleaned.get('trabajadorf')
        if not servicios:
            return cleaned   # sin servicios no hay nada más que validar

        # select_related trae la categoría y el salón de cada servicio en una sola consulta.
        servicios = list(servicios.select_related('categoriaf__establecimientof'))
        # Todos los servicios de una cita deben ser del MISMO salón.
        establecimientos = {s.categoriaf.establecimientof_id for s in servicios}
        if len(establecimientos) > 1:
            raise ValidationError(_('Todos los servicios de la cita deben ser del mismo establecimiento.'))
 
        # salón, servicio y categoría deben estar ACTIVOS.
        for s in servicios:
            if not (s.estado and s.categoriaf.estado and s.categoriaf.establecimientof.estado):
                raise ValidationError(_("El servicio '%(s)s' o su establecimiento está inactivo.") % {'s': s.nombre})

        if trabajadores:
            trabajadores = list(trabajadores)
            for t in trabajadores:
                # El trabajador debe ser del mismo salón de los servicios...
                if t.establecimientof_id not in establecimientos:
                    raise ValidationError(_('El trabajador %(t)s no pertenece a este establecimiento.') % {'t': t})
                
                if not t.estado:
                    raise ValidationError(_('El trabajador %(t)s está inactivo.') % {'t': t})
            # si hay un solo especialista, debe saber hacer TODOS los servicios.
            if len(trabajadores) == 1:
                t = trabajadores[0]
                for s in servicios:
                    if not s.trabajadoresf.filter(pk=t.pk).exists():
                        raise ValidationError(
                            _("%(t)s no está capacitado para el servicio '%(s)s'.") % {'t': t, 's': s.nombre})

        # ---- FECHA Y HORARIO (usa CitaService y FechaCita de services.py) ----
                # ---- FECHA Y HORARIO (usa CitaService y FechaCita de services.py) ----
        fecha = cleaned.get('fecha_cita')
        hora = cleaned.get('hora_inicio')
        estado = cleaned.get('estado')

        # Si falta fecha/hora (Django ya muestra ese error), o la cita está
        # cancelada/desactivada, no se valida: no ocupa agenda.
        if not (fecha and hora) or estado == 'CANCELADA' or not cleaned.get('estadocita', True):
            return cleaned

        # Solo se valida si la cita es nueva o si cambió algo que afecta el horario.
        # Así se puede editar una cita vieja (ej. marcarla COMPLETADA) sin que diga "ya pasó".
        campos_horario = {'fecha_cita', 'hora_inicio', 'serviciof', 'trabajadorf', 'correo_cliente'}
        if self.instance.pk and not (campos_horario & set(self.changed_data)):
            return cleaned

        # No se puede agendar en el pasado.
        if FechaCita.validarHorasFaltantes(fecha, hora) <= 0:
            self.add_error('fecha_cita', _('No se puede agendar una cita en una fecha u hora que ya pasó.'))
            return cleaned

        duracion = sum(s.duracion_minutos for s in servicios)
        establecimiento = servicios[0].categoriaf.establecimientof

        # ---- Salón y especialistas ----
        try:
            # Horario del salón: apertura, cierre y días cerrados (bloque completo).
            CitaService.validar_horario_establecimiento(establecimiento, fecha, hora, duracion)

            if trabajadores:
                # Los servicios se hacen uno tras otro. Cada uno lo atiende el primero
                # de los trabajadores elegidos que sepa hacerlo (misma idea que RN-06),
                # y se valida SOLO su bloque de tiempo, no la duración total.
                hora_bloque = hora
                for srv in servicios:
                    encargado = next(
                        (t for t in trabajadores if srv.trabajadoresf.filter(pk=t.pk).exists()),
                        None)
                    if encargado is None:
                        raise ValidationError(
                            _("Ninguno de los trabajadores elegidos puede realizar '%(s)s'.") % {'s': srv.nombre})
                    # Turno, descanso y choque con otras citas de ese trabajador.
                    CitaService.validar_horario(
                        encargado, fecha, hora_bloque, srv.duracion_minutos,
                        cita_id_actual=self.instance.pk)
                    hora_bloque = FechaCita.sumarMinutos(fecha, hora_bloque, srv.duracion_minutos)
        except ValidationError as err:
            self.add_error('hora_inicio', err)

        # ---- Cliente: no puede tener dos citas cruzadas (RN-03) ----
        try:
            CitaService.validar_choque_cliente(
                cleaned.get('correo_cliente'), fecha, hora, duracion,
                cita_id_actual=self.instance.pk)
        except ValidationError as err:
            self.add_error('correo_cliente', err)

        return cleaned

@admin.register(Cita)
class CitaAdmin(SalonAdminMixin, admin.ModelAdmin):
    form = CitaAdminForm
    list_display = ('codigo_unico', 'nombre_cliente', 'fecha_cita', 'hora_inicio', 'estado',
                    'total_cita', 'anticipo_30', 'nombre_establecimiento')
    list_filter = ('estado', 'fecha_cita', CategoriaListFilter)
    search_fields = ('nombre_cliente', 'correo_cliente', 'telefono_cliente', 'codigo_unico')
    date_hierarchy = 'fecha_cita'   # navegación por año/mes/día arriba de la lista
    readonly_fields = ('codigo_unico', 'creado_el', 'nombre_establecimiento', 'fecha_expiracion',
                       'total_cita', 'anticipo_30', 'hora_fin')
    filter_horizontal = ('serviciof', 'trabajadorf')
    actions = ['cancelar_por_inasistencia']

    # ---- Columnas calculadas con ServicioService.precioServicio ----
    @staticmethod
    def _resumen_precios(obj):
        if not obj.pk:
            return None
        return ServicioService.precioServicio(list(obj.serviciof.all()))

    @admin.display(description=_('Total'))
    def total_cita(self, obj):
        resumen = self._resumen_precios(obj)
        return f"${resumen['suma_total']:,.0f}" if resumen else '-'

    @admin.display(description=_('Anticipo 30%'))
    def anticipo_30(self, obj):
        resumen = self._resumen_precios(obj)
        return f"${resumen['monto_anticipo']:,.0f}" if resumen else '-'

    # ---- Acción: usa CitaService.validarToleranciaDeRetraso ----
    # permissions=['change'] -> solo la ve quien puede EDITAR citas (el Trabajador no).
    @admin.action(description=_('Cancelar por inasistencia (pasados 15 min de tolerancia)'),
                  permissions=['change'])
    def cancelar_por_inasistencia(self, request, queryset):
        canceladas = 0
        for cita in queryset:
            try:
                CitaService.validarToleranciaDeRetraso(cita)
            except ValidationError as err:
                self.message_user(request, f"Cita {cita.codigo_unico}: {'; '.join(err.messages)}",
                                  messages.WARNING)
                continue
            cita.estado = 'CANCELADA'
            cita.save(update_fields=['estado'])
            canceladas += 1
        if canceladas:
            self.message_user(request, _('%(n)d cita(s) cancelada(s) por inasistencia.') % {'n': canceladas},
                              messages.SUCCESS)

    def save_related(self, request, form, formsets, change):
        """
        Se ejecuta DESPUÉS de guardar las relaciones muchos a muchos.
        Cita.save() no puede conocer los servicios porque todavía no están
        guardados en ese momento; por eso el nombre del salón se completa aquí.
        """
        super().save_related(request, form, formsets, change)
        cita = form.instance
        srv = cita.serviciof.select_related('categoriaf__establecimientof').first()
        nombre = srv.categoriaf.establecimientof.nombre if srv else None
        if nombre != cita.nombre_establecimiento:
            # .update() escribe directo en la BD sin volver a ejecutar save().
            Cita.objects.filter(pk=cita.pk).update(nombre_establecimiento=nombre)
 
 

# FACTURACIÓN (cobranza manual: Asistente y Admin)

@admin.register(Factura)
class FacturaAdmin(SalonAdminMixin, admin.ModelAdmin):
    list_display = ('numero_factura', 'citaf', 'metodo_pago', 'total_general', 'pagada', 'fecha_emision')
    list_filter = ('pagada', 'metodo_pago', 'fecha_emision')
    search_fields = ('numero_factura', 'citaf__nombre_cliente', 'citaf__codigo_unico')
    # Los montos los calcula el sistema a partir de los servicios de la cita: nadie los escribe a mano.
    readonly_fields = ('numero_factura', 'nombre_establecimiento', 'fecha_emision',
                       'monto_anticipo_30', 'monto_restante_70', 'subtotal', 'total_general')

    def save_model(self, request, obj, form, change):
        servicios = list(obj.citaf.serviciof.select_related('categoriaf__establecimientof'))
        # Completa el nombre del salón tomándolo de los servicios de la cita.
        obj.nombre_establecimiento = servicios[0].categoriaf.establecimientof.nombre if servicios else None
        # Montos con ServicioService.precioServicio (30% / 70%).
        resumen = ServicioService.precioServicio(servicios)
        obj.subtotal = resumen['suma_total']
        obj.monto_anticipo_30 = resumen['monto_anticipo']
        obj.monto_restante_70 = resumen['monto_restante']
        obj.total_general = obj.subtotal + (obj.total_impuestos or 0)
        super().save_model(request, obj, form, change)

@admin.register(FacturaDetalle)
class FacturaDetalleAdmin(SalonAdminMixin, admin.ModelAdmin):
    list_display = ('facturaf', 'descripcion_item', 'cantidad', 'valor_unitario', 'subtotal_item')
    search_fields = ('descripcion_item', 'facturaf__numero_factura')