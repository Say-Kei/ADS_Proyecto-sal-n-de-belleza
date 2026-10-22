from django.urls import path
from .views import ConsultarComisionesTrabajadorView
from . import views

urlpatterns = [
    path(
        'comisiones/mis-comisiones/',
        ConsultarComisionesTrabajadorView.as_view(),
        name='mis-comisiones'
    ),
    path ('', views.index, name='central'),
    path ('salon/', views.salones, name='inicio'),
    path('citas/', views.salones_citas, name='escoger-cita'),
    path('servicios/', views.salones_servicios, name='servicios'),
    path('ubicacion/', views.salones_ubicacion, name='ubicacion')
]