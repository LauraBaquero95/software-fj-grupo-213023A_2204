# -*- coding: utf-8 -*-
# Archivo: alquiler_equipo.py
# Clase AlquilerEquipo: servicio de alquiler de equipos. Se cobra por día más un depósito.
from src.excepciones.errores import ServicioInvalidoError
from src.modelos.servicio import Servicio
from src.utilidades.validadores import validar_numero_positivo


class AlquilerEquipo(Servicio):
    """Equipo que se puede alquilar. Se permite de 1 a 30 días."""

    DURACION_MINIMA = 1
    DURACION_MAXIMA = 30

    def __init__(self, identificador, nombre, tarifa_dia, deposito=0, disponible=True):
        # Igual que las otras clases hijas: primero el constructor del padre
        super().__init__(identificador, nombre, disponible)
        try:
            tarifa = validar_numero_positivo(tarifa_dia, "tarifa por día")
            # El depósito puede ser 0, por eso permitir_cero=True
            deposito_validado = validar_numero_positivo(
                deposito, "depósito", permitir_cero=True
            )
        except ValueError as error:
            raise ServicioInvalidoError(f"Datos del equipo inválidos: {error}") from error
        self.__tarifa_dia = tarifa
        self.__deposito = deposito_validado

    @property
    def tarifa_dia(self):
        return self.__tarifa_dia

    @property
    def deposito(self):
        return self.__deposito

    def validar_parametros(self, duracion):
        # El método estático del padre ya revisa que sea entero (y no bool) y el rango.
        # Antes había aquí una revisión duplicada que lanzaba ServicioInvalidoError (FJ-102);
        # una duración incorrecta es un error de reserva (FJ-104), como en las otras clases.
        self._validar_rango_duracion(
            duracion, self.DURACION_MINIMA, self.DURACION_MAXIMA, "días"
        )

    def _costo_base(self, duracion):
        # Costo base = tarifa por día x días + depósito
        return self.__tarifa_dia * duracion + self.__deposito

    def describir(self):
        return (f"{super().describir()} - "
                f"${self.tarifa_dia:,.0f}/día, "
                f"depósito ${self.deposito:,.0f}")
