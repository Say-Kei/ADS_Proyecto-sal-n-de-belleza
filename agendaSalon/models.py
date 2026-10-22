from decimal import Decimal
from datetime import datetime, timedelta
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.html import format_html
from django.core.exceptions import ValidationError
import uuid
from django.db.models import Sum
from django.utils import timezone

# 1. ESTABLECIMIENTO
class Establecimiento(models.Model):
    REGIMEN_CHOICES = (
        ('NO_RESPONSABLE_IVA', 'No Responsable de IVA'),
        ('RESPONSABLE_IVA', 'Responsable de IVA'),
        ('REGIMEN_SIMPLE', 'Régimen Simple de Tributación'),
    )

    id_establecimiento = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=150, unique=True, verbose_name="Nombre Comercial")
    slug = models.SlugField(max_length=160, unique=True, blank=True, editable=False)
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción del Negocio")
    razon_social = models.CharField(max_length=150, blank=True, null=True, verbose_name="Razón Social / Nombre Legal")
    nit = models.CharField(max_length=20, unique=True, null=True, blank=True, verbose_name="NIT / Identificación")
    representante_legal = models.CharField(max_length=150, blank=True, null=True)
    regimen_tributario = models.CharField(max_length=30, choices=REGIMEN_CHOICES, default='NO_RESPONSABLE_IVA')
    direccion = models.CharField(max_length=255, verbose_name="Dirección Física")
    ciudad = models.CharField(max_length=100, default="Quibdó")
    departamento = models.CharField(max_length=100, default="Chocó")
    telefono = models.CharField(max_length=30, verbose_name="Teléfono / WhatsApp")
    correo = models.EmailField(unique=True, verbose_name="Correo Electrónico")
    logo = models.ImageField(upload_to='establecimientos/logos/', blank=True, null=True)
    imagen_portada = models.ImageField(upload_to='establecimientos/portadas/', blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True, editable=False)
    codigo_unico = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    estado = models.BooleanField(default=True)
    objects=models.Manager()

    class Meta:
        db_table = 'establecimiento'
        verbose_name = 'Establecimiento'
        verbose_name_plural = 'Establecimientos'
        ordering = ['nombre']        

    def save(self, *args, **kwargs):
        slug_actual = getattr(self, 'slug', None)
        nombre_actual = getattr(self, 'nombre', '')
        if not slug_actual and nombre_actual:
            self.slug = slugify(nombre_actual)
            slug_original = self.slug
            contador = 1
            while Establecimiento.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{slug_original}-{contador}"
                contador += 1
        super().save(*args, **kwargs)

    def __str__(self):
        nit_val = getattr(self, 'nit', None)
        nombre_val = getattr(self, 'nombre', 'Establecimiento')
        return f"{nombre_val} (NIT: {nit_val})" if nit_val else nombre_val


# 2. PERFIL DE USUARIO
class PerfilUsuario(models.Model):
    class RolChoices(models.TextChoices):
        SUPERADMIN = 'SUPERADMIN', 'Superadministrador / Desarrollador'
        ADMIN_NEGOCIO = 'ADMIN_NEGOCIO', 'Administrador de Salón'
        ASISTENTE = 'ASISTENTE', 'Asistente / Recepcionista'
        TRABAJADOR = 'TRABAJADOR', 'Empleado / Especialista'
        CLIENTE = 'CLIENTE', 'Cliente'

    ROLES_CON_ESTABLECIMIENTO = ('ADMIN_NEGOCIO', 'ASISTENTE', 'TRABAJADOR')
    ROLES_SIN_ESTABLECIMIENTO = ('SUPERADMIN', 'CLIENTE')

    id_perfil = models.AutoField(primary_key=True)
    usuariof = models.OneToOneField(User, on_delete=models.CASCADE, db_column='id_usuario', related_name='fperfil', verbose_name='Usuario')
    establecimientof = models.ForeignKey(Establecimiento, on_delete=models.CASCADE, db_column='id_establecimiento', related_name='fpersonal', verbose_name='Establecimiento')
    nombre_establecimiento = models.CharField(max_length=150, blank=True, null=True, editable=False)
    rol = models.CharField(max_length=20, choices=RolChoices, default=RolChoices.TRABAJADOR)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    porcentaje_comision = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00')), 
                    MaxValueValidator(Decimal('100.00'))]
    )
    imagen = models.ImageField(upload_to='trabajadores/', max_length=255, blank=True, null=True)
    estado = models.BooleanField(default=True)
    objects=models.Manager()
    codigo_unico = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    class Meta:
        db_table = 'perfil_usuario'
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuarios'

    def clean(self):
        """Reglas de coherencia rol <-> establecimiento."""
        errores = {}
        if self.rol in self.ROLES_CON_ESTABLECIMIENTO and not self.establecimientof_id:
            errores['establecimientof'] = 'Este rol debe estar asociado a un establecimiento.'
        if self.rol in self.ROLES_SIN_ESTABLECIMIENTO and self.establecimientof_id:
            errores['establecimientof'] = 'El Superadministrador no pertenece a un establecimiento.'
        if self.usuariof_id and self.usuariof.is_superuser and self.rol != self.RolChoices.SUPERADMIN:
            errores['rol'] = 'Un superusuario de Django debe tener el rol Superadministrador.'
        if errores:
            raise ValidationError(errores)

    def _sincronizar_usuario(self):
        """Mantiene is_staff / is_superuser del User alineados con el rol."""
        usr = self.usuariof
        campos = []
        # Todos los roles que existen trabajan en el panel (el cliente no tiene cuenta).
        debe_ser_staff = True
        if usr.is_staff != debe_ser_staff and not usr.is_superuser:
            usr.is_staff = debe_ser_staff
            campos.append('is_staff')
        if self.rol == self.RolChoices.SUPERADMIN:
            if not usr.is_superuser:
                usr.is_superuser = True
                campos.append('is_superuser')
            if not usr.is_staff:
                usr.is_staff = True
                campos.append('is_staff')
        if campos:
            usr.save(update_fields=campos) # pylint: disable=no-member

    def save(self, *args, **kwargs):
        self.clean()
        est = getattr(self, 'establecimientof', None)
        self.nombre_establecimiento = getattr(est, 'nombre', '') if est else None
        super().save(*args, **kwargs)
        self._sincronizar_usuario()

    def __str__(self):
        usr = getattr(self, 'usuariof', None)
        nombre_usr = (getattr(usr, 'get_full_name', lambda: '')() or getattr(usr, 'username', '')) if usr else 'Sin Usuario'
        rol_disp = getattr(self, 'get_rol_display', lambda: '')()
        nombre_est = getattr(self, 'nombre_establecimiento', '') or 'Plataforma'
        return f"{nombre_usr} - {rol_disp} ({nombre_est})"

    @property
    def es_superadmin(self):
        usr = getattr(self, 'usuariof', None)
        is_super = getattr(usr, 'is_superuser', False) if usr else False
        return self.rol == self.RolChoices.SUPERADMIN or is_super

    @property
    def es_admin_local(self):
        return self.rol == self.RolChoices.ADMIN_NEGOCIO

    @property
    def es_asistente(self):
        return self.rol == self.RolChoices.ASISTENTE

    @property
    def es_trabajador(self):
        return self.rol == self.RolChoices.TRABAJADOR

    @property
    def es_personal_interno(self):
        return self.rol in self.ROLES_CON_ESTABLECIMIENTO

# 3. HORARIO ESTABLECIMIENTO
class HorarioEstablecimiento(models.Model):
    DIAS_SEMANA = (
        (1, 'Lunes'), (2, 'Martes'), (3, 'Miércoles'),
        (4, 'Jueves'), (5, 'Viernes'), (6, 'Sábado'), (7, 'Domingo'),
    )

    id_horario = models.AutoField(primary_key=True)
    establecimientof = models.ForeignKey(Establecimiento, on_delete=models.CASCADE, db_column='id_establecimiento', related_name='fhorarios_establecimiento', verbose_name='Establecimiento')
    dia_semana = models.IntegerField(choices=DIAS_SEMANA)
    hora_apertura = models.TimeField(blank=True, null=True)
    hora_cierre = models.TimeField(blank=True, null=True)
    cerrado = models.BooleanField(default=False)
    objects=models.Manager()

    class Meta:
        db_table = 'horario_establecimiento'
        unique_together = ('establecimientof', 'dia_semana')

    def __str__(self):
        cerrado_val = getattr(self, 'cerrado', False)
        h_ap = getattr(self, 'hora_apertura', '')
        h_ci = getattr(self, 'hora_cierre', '')
        estado_str = "Cerrado" if cerrado_val else f"{h_ap} - {h_ci}"
        est = getattr(self, 'establecimientof', None)
        nombre_est = getattr(est, 'nombre', '') if est else ''
        dia_disp = getattr(self, 'get_dia_semana_display', lambda: '')()
        return f"{dia_disp} ({estado_str}) - {nombre_est}"


# 4. HORARIO TRABAJADOR
class HorarioTrabajador(models.Model):
    id_horario_trabajador = models.AutoField(primary_key=True)
    trabajadorf = models.ForeignKey(PerfilUsuario, on_delete=models.CASCADE, db_column='id_perfil', related_name='fhorarios_trabajador', verbose_name='Trabajador')
    dia_semana = models.IntegerField(choices=HorarioEstablecimiento.DIAS_SEMANA)
    hora_entrada = models.TimeField()
    hora_salida = models.TimeField()
    descanso_inicio = models.TimeField(blank=True, null=True)
    descanso_fin = models.TimeField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    objects=models.Manager()
    class Meta:
        db_table = 'horario_trabajador'
        unique_together = ('trabajadorf', 'dia_semana')

    


# 5. CATEGORÍA
class Categoria(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    establecimientof = models.ForeignKey(Establecimiento, on_delete=models.CASCADE, db_column='id_establecimiento', related_name='fcategorias')
    nombre_establecimiento = models.CharField(max_length=150, blank=True, null=True, editable=False)
    nombre = models.CharField(max_length=80)
    estado = models.BooleanField(default=True)
    objects= models.Manager()

    class Meta:
        db_table = 'categoria'

    def save(self, *args, **kwargs):
        est = getattr(self, 'establecimientof', None)
        if est:
            self.nombre_establecimiento = getattr(est, 'nombre', '')
        super().save(*args, **kwargs)

    def __str__(self):
        nombrecategoria = getattr(self, 'nombre', 'categoria indefinida')
        nombre_est = getattr(self, 'nombre_establecimiento')
        return f"{nombrecategoria} - {nombre_est}"

# 6. SERVICIO
class Servicio(models.Model):
    id_servicio = models.AutoField(primary_key=True)
    categoriaf = models.ForeignKey(Categoria, on_delete=models.CASCADE, db_column='id_categoria', related_name='fservicios', verbose_name='Categoria')
    nombre_establecimiento = models.CharField(max_length=150, blank=True, null=True, editable=False)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Precio en COP"
    )
    duracion_minutos = models.IntegerField(help_text="Duración estimada en minutos")
    trabajadoresf = models.ManyToManyField(PerfilUsuario, related_name='fservicios_asociados', blank=False, verbose_name='Trabajadore')
    imagen = models.ImageField(upload_to='servicios/', max_length=255, blank=True, null=True)
    estado = models.BooleanField(default=True)
    objects=models.Manager()
    codigo_unico = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)


    class Meta:
        db_table = 'servicio'
        unique_together = ('nombre', 'categoriaf')
        
    def __str__(self):
        return f"{self.nombre} - {self.precio_formateado} ({self.duracion_minutos} min)"

    @property
    def establecimientof(self):
        cat = getattr(self, 'categoriaf', None)
        return getattr(cat, 'establecimientof', None) if cat else None

    @property
    def precio_formateado(self):
        p = getattr(self, 'precio', Decimal('0.00'))
        return f"${p:,.0f}" if p else "$0"

    def save(self, *args, **kwargs):
        cat = getattr(self, 'categoriaf', None)
        est = getattr(cat, 'establecimientof', None) if cat else None
        if est:
            self.nombre_establecimiento = getattr(est, 'nombre', '')
        super().save(*args, **kwargs)


# 7. CITA
class Cita(models.Model):
    ESTADOS = (
        ('PENDIENTE', 'Pendiente de Anticipo'),
        ('CONFIRMADA', 'Confirmada (30% Pagado)'),
        ('PAGO COMPLETO', 'Pago Completo (100% Pagado)'),
        ('COMPLETADA', 'Completada'),
        ('CANCELADA', 'Cancelada'),
    )

    id_cita = models.AutoField(primary_key=True)
    serviciof = models.ManyToManyField(
    Servicio, 
    related_name='fcitas',blank=False, verbose_name='Servicio'
)
    trabajadorf = models.ManyToManyField(PerfilUsuario, related_name='fcitas_asignadas', blank=False, verbose_name='Trabajador')
    nombre_establecimiento = models.CharField(max_length=150, blank=True, null=True, editable=False)
    nombre_cliente = models.CharField(max_length=120)
    correo_cliente = models.EmailField()
    telefono_cliente = models.CharField(max_length=20)
    fecha_cita = models.DateField()
    hora_inicio = models.TimeField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')
    fecha_expiracion = models.DateTimeField(null=True, blank=True, help_text="Límite de 7 minutos para pago de anticipo")
    nota = models.TextField(blank=True, null=True)
    creado_el = models.DateTimeField(auto_now_add=True)
    codigo_unico = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    estadocita=models.BooleanField(default=True)
    objects = models.Manager()

    class Meta:
        db_table = 'cita'
        ordering = ['-fecha_cita', '-hora_inicio']

    def __str__(self):
        codigo = getattr(self, 'codigo_unico')
        nombre_establecimiento = getattr(self, 'nombre_establecimiento')
        cliente = getattr(self, 'nombre_cliente')
        estadocita = getattr(self, 'estado')
        return f"{codigo} - {nombre_establecimiento} - {cliente} - {estadocita}"

    def saltos_multilinea(self):
        codigo = getattr(self, 'codigo_unico')
        nombre_establecimiento = getattr(self, 'nombre_establecimiento')
        cliente = getattr(self, 'nombre_cliente')
        estadocita = getattr(self, 'estado')

        return format_html(
            codigo,
            nombre_establecimiento,
            cliente,
            estadocita
        )

    @property
    def duracion_total(self):
        """Suma de minutos de TODOS los servicios de la cita."""
        if not self.pk:
            return 0
        return self.serviciof.aggregate(total=Sum('duracion_minutos'))['total'] or 0

    @property
    def hora_fin(self):
        if self.hora_inicio and self.fecha_cita and self.duracion_total:
            inicio_dt = datetime.combine(self.fecha_cita, self.hora_inicio)
            return (inicio_dt + timedelta(minutes=self.duracion_total)).time()
        return None

    @property
    def precio_servicio(self):
        """Suma de precios de TODOS los servicios de la cita."""
        if not self.pk:
            return Decimal('0.00')
        return self.serviciof.aggregate(total=Sum('precio'))['total'] or Decimal('0.00')

    def save(self, *args, **kwargs):
        # Solo al CREAR la cita (no al editarla), si está pendiente y no trae fecha:
        if self._state.adding and self.estado == 'PENDIENTE' and not self.fecha_expiracion:
            self.fecha_expiracion = timezone.now() + timedelta(minutes=7)
        super().save(*args, **kwargs)
    @property
    def rango_horario_formateado(self):
        """Devuelve el rango de horario formateado en formato 12 horas (ej: 08:00 AM - 05:00 PM)."""
        h_ini = getattr(self, 'hora_inicio', None)
        h_fin = getattr(self, 'hora_fin', None)

        if hasattr(h_ini, 'strftime') and hasattr(h_fin, 'strftime'):
            # pylint: disable=no-member
            return f"{h_ini.strftime('%I:%M %p')} - {h_fin.strftime('%I:%M %p')}"
        return ""

    @property
    def valor_anticipo_30(self):
        return self.precio_servicio * Decimal('0.30')

    @property
    def valor_restante_70(self):
        return self.precio_servicio * Decimal('0.70')



# 8. RESEÑA
class Resena(models.Model):
    id_resena = models.AutoField(primary_key=True)
    citaf = models.OneToOneField(Cita, on_delete=models.CASCADE, db_column='id_cita', related_name='fresena')
    nombre_establecimiento = models.CharField(max_length=150, blank=True, null=True, editable=False)
    calificacion = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comentario = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.BooleanField(default=True)
    objects=models.Manager()

    class Meta:
        db_table = 'resena'


# 9. FACTURA
class Factura(models.Model):
    METODOS_PAGO = (
        ('EFECTIVO', 'Efectivo en local'),
        ('TRANSFERENCIA', 'Transferencia / Bre-B / Nequi / Daviplata'),
        ('TARJETA', 'Tarjeta Crédito / Débito'),
    )

    id_factura = models.AutoField(primary_key=True)
    citaf = models.OneToOneField(Cita, on_delete=models.CASCADE, db_column='id_cita', related_name='ffactura')
    nombre_establecimiento = models.CharField(max_length=150, blank=True, null=True, editable=False)
    numero_factura = models.CharField(max_length=50, unique=True, blank=True, editable=False)

    monto_anticipo_30 = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, validators=[MinValueValidator(Decimal('0.00'))])
    monto_restante_70 = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, validators=[MinValueValidator(Decimal('0.00'))])
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, validators=[MinValueValidator(Decimal('0.00'))])
    total_impuestos = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, validators=[MinValueValidator(Decimal('0.00'))])
    total_general = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, validators=[MinValueValidator(Decimal('0.00'))])
    
    metodo_pago = models.CharField(max_length=20, choices=METODOS_PAGO, default='EFECTIVO')
    pagada = models.BooleanField(default=False)
    fecha_emision = models.DateTimeField(auto_now_add=True)
    estado = models.BooleanField(default=True)
    objects=models.Manager()

    class Meta:
        db_table = 'factura'

    def save(self, *args, **kwargs):
        if not getattr(self, 'numero_factura', None):
            self.numero_factura = f"FAC-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


# 10. DETALLE DE FACTURA
class FacturaDetalle(models.Model):
    id_detalle = models.AutoField(primary_key=True)
    facturaf = models.ForeignKey(Factura, on_delete=models.CASCADE, db_column='id_factura', related_name='fdetalles')
    descripcion_item = models.CharField(max_length=200)
    cantidad = models.IntegerField(default=1)
    valor_unitario = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    subtotal_item = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    estado = models.BooleanField(default=True)
    objects=models.Manager()

    class Meta:
        db_table = 'factura_detalle'