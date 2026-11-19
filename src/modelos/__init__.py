# -*- coding: utf-8 -*-
# Convierte la carpeta en paquete y reexporta las clases del modelo, para poder escribir:
#   from src.modelos import Cliente, Reserva
from .entidad_base import EntidadBase
from .cliente import Cliente
from .servicio import Servicio
from .reserva_sala import ReservaSala
from .alquiler_equipo import AlquilerEquipo
from .asesoria import AsesoriaEspecializada
from .reserva import EstadoReserva, Reserva

__all__ = [
    "EntidadBase",
    "Cliente",
    "Servicio",
    "ReservaSala",
    "AlquilerEquipo",
    "AsesoriaEspecializada",
    "EstadoReserva",
    "Reserva",
]
