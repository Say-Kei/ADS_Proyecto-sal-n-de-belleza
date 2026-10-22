from rest_framework.permissions import BasePermission, SAFE_METHODS

from .models import (
    Establecimiento,
    PerfilUsuario,
    Categoria,
    Servicio,
    HorarioEstablecimiento,
    HorarioTrabajador,
    Cita,
    Factura,
    FacturaDetalle,
    Resena,
)

Rol = PerfilUsuario.RolChoices

VER = 'view'          # ver / consultar
AGREGAR = 'add'       # crear uno nuevo
CAMBIAR = 'change'    # editar uno existente
ELIMINAR = 'delete'    # eliminar uno existente

PERMISOS_POR_ROL = {
    Rol.SUPERADMIN: {
        'establecimiento': {VER, AGREGAR, CAMBIAR},
        'perfilusuario': {VER, AGREGAR, CAMBIAR},
        'categoria': {VER, AGREGAR, CAMBIAR},
        'servicio': {VER, AGREGAR, CAMBIAR},
        'horarioestablecimiento': {VER, AGREGAR, CAMBIAR},
        'horariotrabajador': {VER, AGREGAR, CAMBIAR},
        'cita': {VER, AGREGAR, CAMBIAR},
        'factura': {VER, AGREGAR, CAMBIAR},
        'facturadetalle': {VER, AGREGAR, CAMBIAR},
        'resena': {VER, AGREGAR, CAMBIAR},
    },
    Rol.ADMIN_NEGOCIO: {
        'establecimiento': {VER, CAMBIAR},
        'perfilusuario': {VER, AGREGAR, CAMBIAR},
        'categoria': {VER, AGREGAR, CAMBIAR},
        'servicio': {VER, AGREGAR, CAMBIAR},
        'horarioestablecimiento': {VER, AGREGAR, CAMBIAR},
        'horariotrabajador': {VER, AGREGAR, CAMBIAR},
        'cita': {VER, AGREGAR, CAMBIAR},
        'factura': {VER, AGREGAR, CAMBIAR},
        'facturadetalle': {VER, AGREGAR, CAMBIAR},
        'resena': {VER, AGREGAR, CAMBIAR},
    },
    Rol.ASISTENTE: {
        'establecimiento': {VER},
        'perfilusuario': {VER},
        'categoria': {VER},
        'servicio': {VER},
        'horarioestablecimiento': {VER},
        'horariotrabajador': {VER},
        'cita': {VER, AGREGAR, CAMBIAR},
        'factura': {VER, AGREGAR, CAMBIAR},
        'facturadetalle': {VER, AGREGAR, CAMBIAR},
        'resena': {VER, AGREGAR, CAMBIAR},
    },
    Rol.TRABAJADOR: {
        'perfilusuario': {VER},
        'horariotrabajador': {VER},
        'cita': {VER},
    },

}

PERMISOS_ESPECIALES = {
    'gestionar_ciclo_de_establecimiento': {Rol.SUPERADMIN},
    'gestionar_ciclo_de_trabajadores': {Rol.SUPERADMIN, Rol.ADMIN_NEGOCIO},
    'ver_reportes_ganancias': {Rol.SUPERADMIN, Rol.ADMIN_NEGOCIO},
    'ver_comisiones': {Rol.ADMIN_NEGOCIO},
} 

ROLES_ASIGNABLES ={
    Rol.SUPERADMIN: {Rol.ADMIN_NEGOCIO, Rol.ASISTENTE, Rol.TRABAJADOR},
    Rol.ADMIN_NEGOCIO: {Rol.ASISTENTE, Rol.TRABAJADOR},
    Rol.ASISTENTE: {Rol.TRABAJADOR},
}

def obtener_perfil(user):
    if user is None or not getattr(user, 'is_authenticated', False):
        return None
    return getattr(user, 'fperfil', None)

def obtener_rol(user):
    # Sin sesión o con la cuenta desactivada: sin rol (sin acceso).
    if user is None or not getattr(user, 'is_authenticated', False) or not user.is_active:
        return None

    if user.is_superuser:
        return Rol.SUPERADMIN

    perfil = obtener_perfil(user)
    if perfil is None or not perfil.estado:
        return None

    # El Superadmin no tiene salón (None). Si SÍ tiene salón y está inactivo,
    # se le corta el acceso (RN-11). Antes decía `is None and not ...estado`,
    # que da error cuando no hay salón y nunca bloqueaba un salón inactivo.
    establecimiento = perfil.establecimientof
    if establecimiento is not None and not establecimiento.estado:
        return None

    return perfil.rol

def obtener_establecimiento(user):
    perfil = obtener_perfil(user)
    return perfil.establecimientof if perfil else None

def es_superadmin(user):
    return obtener_rol(user) == Rol.SUPERADMIN

def tiene_permiso(user, modelo, accion):
    rol = obtener_rol(user)
    if rol is None:
        return False
    return accion in PERMISOS_POR_ROL.get(rol, {}).get(modelo, set())

def tiene_algun_permiso(user, modelo):
    rol = obtener_rol(user)
    if rol is None:
        return False
    return bool(PERMISOS_POR_ROL.get(rol, {}).get(modelo))

def tiene_permiso_especial(user, nombre):
    return obtener_rol(user) in PERMISOS_ESPECIALES.get(nombre, set())

def roles_asignables(user):
    return ROLES_ASIGNABLES.get(obtener_rol(user),())

def acceso_admin(user):
    rol = obtener_rol(user)
    return bool(rol) and user.is_staff

#AISLAMIENTO MULTI-TENANT: un usuario solo puede ver lo que pertenece a su establecimiento

LOOKUP_ESTABLECIMIENTO = {
    'establecimiento': 'pk',   # el establecimiento ya ES el salón (pk = llave primaria)
    'perfilusuario': 'establecimientof',
    'categoria': 'establecimientof',
    'servicio': 'categoriaf__establecimientof',
    'horarioestablecimiento': 'establecimientof',
    'horariotrabajador': 'trabajadorf__establecimientof',
    'cita': 'serviciof__categoriaf__establecimientof',
    'factura': 'citaf__serviciof__categoriaf__establecimientof',
    'facturadetalle': 'facturaf__citaf__serviciof__categoriaf__establecimientof',
    'resena': 'citaf__serviciof__categoriaf__establecimientof',
}

LOOKUP_PROPIO_TRABAJADOR = {
    'perfilusuario': 'pk',               # su propio perfil
    'horariotrabajador': 'trabajadorf',  # sus propios horarios
    'cita': 'trabajadorf',               # las citas que le asignaron a él
}

MODELOS_CON_ESTABLECIMIENTO = {
    Establecimiento, PerfilUsuario, Categoria, Servicio, HorarioEstablecimiento,
    HorarioTrabajador, Cita, Factura, FacturaDetalle, Resena,
}

def filtrar_query_por_user(queryset, user):
    rol = obtener_rol(user)

    # Sin rol válido (inactivo, anónimo...): no ve nada.
    # OJO: antes decía `if not rol is None`, que es al revés: dejaba SIN datos a
    # quien SÍ tenía rol (incluido el Superadmin) y por eso la lista salía vacía.
    if rol is None:
        return queryset.none()

    # El Superadmin ve todo, sin filtro.
    if rol == Rol.SUPERADMIN:
        return queryset

    modelo = queryset.model._meta.model_name
    perfil = obtener_perfil(user)
    # _default_manager = el "objects" del modelo (para armar la subconsulta).
    manager = queryset.model._default_manager

    if rol in (Rol.ADMIN_NEGOCIO, Rol.ASISTENTE):
        lookup = LOOKUP_ESTABLECIMIENTO.get(modelo)
        if not lookup or perfil is None or not perfil.establecimientof_id:
            return queryset.none()

        # Se compara con el id del SALÓN (perfil.establecimientof_id), no con el id
        # del perfil (perfil.pk): son números distintos y daban resultados erróneos.
        subconsulta = manager.filter(**{lookup: perfil.establecimientof_id}).values('pk')
        return queryset.filter(pk__in=subconsulta)

    # TRABAJADOR: solo lo que es suyo (su perfil, su horario y sus citas).
    if rol == Rol.TRABAJADOR:
        lookup = LOOKUP_PROPIO_TRABAJADOR.get(modelo)
        if not lookup or perfil is None:
            return queryset.none()
        subconsulta = manager.filter(**{lookup: perfil.pk}).values('pk')
        return queryset.filter(pk__in=subconsulta)

    return queryset.none()  # los demás roles no tienen acceso a nada

def _cita_de(obj):
    if isinstance(obj, Cita):
        return obj
    if isinstance(obj, FacturaDetalle):
        return obj.facturaf.citaf
    return getattr(obj, 'citaf', None)

def establecimiento_id_de(obj):
    """Devuelve el id del salón al que pertenece cualquier registro (o None)."""
    if isinstance(obj, Establecimiento):
        return obj.pk
    if isinstance(obj, (PerfilUsuario, Categoria, HorarioEstablecimiento)):
        return obj.establecimientof_id
    if isinstance(obj, Servicio):
        return obj.categoriaf.establecimientof_id
    if isinstance(obj, HorarioTrabajador):
        return obj.trabajadorf.establecimientof_id
    if isinstance(obj, (Cita, Factura, FacturaDetalle, Resena)):
        cita = _cita_de(obj)
        if cita is None:
            return None
        # La cita no guarda el salón directo: se obtiene por sus servicios.
        return cita.serviciof.values_list('categoriaf__establecimientof_id', flat=True).first()
    return None

def puede_acceder_objeto(user, obj):
    """¿Este usuario puede tocar ESTE registro? (aplica el aislamiento por rol)."""
    rol = obtener_rol(user)
    if rol is None:
        return False
    if rol == Rol.SUPERADMIN:
        return True
 
    perfil = obtener_perfil(user)
    if perfil is None:
        return False
 
    # ADMIN y ASISTENTE: el registro debe ser de su mismo salón.
    if rol in (Rol.ADMIN_NEGOCIO, Rol.ASISTENTE):
        est_id = establecimiento_id_de(obj)
        return est_id is not None and est_id == perfil.establecimientof_id
 
    # TRABAJADOR: solo su perfil, sus horarios o sus citas.
    if rol == Rol.TRABAJADOR:
        if isinstance(obj, PerfilUsuario):
            return obj.pk == perfil.pk
        if isinstance(obj, HorarioTrabajador):
            return obj.trabajadorf_id == perfil.pk
        if isinstance(obj, Cita):
            return obj.trabajadorf.filter(pk=perfil.pk).exists()
        return False

    # Cualquier otro caso: sin acceso.
    return False

METODO_A_ACCION = {
    'GET': VER, 'HEAD': VER, 'OPTIONS': VER,
    'POST': AGREGAR,
    'PUT': CAMBIAR, 'PATCH': CAMBIAR,
    'DELETE': ELIMINAR,
}

class TieneRolActivo(BasePermission):
    """
    Permite el acceso solo a usuarios con un rol activo y un establecimiento activo.
    """

    message ='Su cuenta, perfil o establecimiento se encuentra inactivo.'

    def has_permission(self, request, view):
        return obtener_rol(request.user) is not None

def roles_permitidos(*roles):
    roles=set(roles)

    class _RolPermitido(BasePermission):
        message = f'Su rol no tiene permiso para esta acción. Roles permitidos: {roles}.'

        def has_permission(self, request, view):
            return obtener_rol(request.user) in roles

    _RolPermitido.__name__ = 'RolPermitido_' + '_'.join(sorted(str(r) for r in roles))
    return _RolPermitido    

# Atajos ya listos para usar en las vistas.
EsSuperAdmin = roles_permitidos(Rol.SUPERADMIN)
EsAdminNegocio = roles_permitidos(Rol.ADMIN_NEGOCIO)
EsPersonalInterno = roles_permitidos(Rol.SUPERADMIN, Rol.ADMIN_NEGOCIO, Rol.ASISTENTE, Rol.TRABAJADOR)
EsAdminOAsistente = roles_permitidos(Rol.ADMIN_NEGOCIO, Rol.ASISTENTE)
EsTrabajador = roles_permitidos(Rol.TRABAJADOR)

class PuedeVerReportesGanancias(BasePermission):
    """solo los roles autorizados pueden ver los reportes de ganancias."""
    message = 'No tiene permiso para ver reportes de ganancias.'
 
    def has_permission(self, request, view):
        return tiene_permiso_especial(request.user, 'ver_reportes_ganancias')

class PermisoPorModelo(BasePermission):

    message = 'No tiene permiso para esta acción en este modelo.'

    def has_permission(self, request, view):
        modelo = getattr(view, 'permiso_modelo', None)
        accion = METODO_A_ACCION.get(request.method)
        if modelo is None or accion is None:
            return False
        return tiene_permiso(request.user, modelo, accion)

    def has_object_permission(self, request, view, obj):
        return puede_acceder_objeto(request.user, obj)

class SoloLectura(BasePermission):

    def has_permission(self, request, view):
        return obtener_rol(request.user) is not None

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return puede_acceder_objeto(request.user, obj)
 