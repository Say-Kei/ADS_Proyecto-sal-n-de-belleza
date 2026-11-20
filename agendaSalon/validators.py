from django.core.exceptions import ValidationError


def validar_usuario_activo(usuario):
    if usuario is None:
        raise ValidationError("No existe")
    elif not getattr(usuario, 'is_authenticated', False):
        raise ValidationError("No esta autentificado")
    elif not usuario.is_active:
        raise ValidationError("No esta activo el usuario")
    return True