# -*- coding: utf-8 -*-
# Archivo: gestor_fj.py
# Clase GestorFJ: administra clientes, servicios y reservas usando listas internas.

from src.excepciones import (
    ErrorGestion,
    ClienteInvalidoError,
    ServicioNoDisponibleError,
    ReservaInvalidaError,
    OperacionNoPermitidaError,
)
# Se importa desde cada módulo (y no desde el paquete) para no depender de lo que
# exporte src/modelos/__init__.py.
from src.modelos.cliente import Cliente
from src.modelos.reserva import Reserva
from src.modelos.servicio import Servicio
# CORRECCIÓN: antes se hacía logging.getLogger("SoftwareFJ") a secas, y así el logger
# no tenía manejador: nada se escribía en logs/sistema.log. obtener_logger() lo
# configura (archivo, formato y nivel) y evita manejadores duplicados.
from src.utilidades.logger import describir_error, obtener_logger

logger = obtener_logger()


class GestorFJ:
    """Administra clientes, servicios y reservas usando listas internas."""

    def __init__(self):
        self._clientes = []
        self._servicios = []
        self._reservas = []
        logger.info("GestorFJ iniciado")

    # ---------- consultas: devuelven copias para proteger las listas internas ----------
    @property
    def clientes(self):
        return list(self._clientes)

    @property
    def servicios(self):
        return list(self._servicios)

    @property
    def reservas(self):
        return list(self._reservas)

    # ---------- búsquedas ----------
    # CORRECCIÓN: las entidades exponen `identificador` (ver EntidadBase), no `id`.
    # Con `.id` se lanzaba AttributeError y, como los métodos de registro capturan
    # Exception, todo fallaba en silencio devolviendo None.
    def buscar_cliente(self, id_cliente):
        for cliente in self._clientes:
            if cliente.identificador == id_cliente:
                return cliente
        raise ClienteInvalidoError(f"No se encontró cliente con Id '{id_cliente}'")

    def buscar_servicio(self, id_servicio):
        for servicio in self._servicios:
            if servicio.identificador == id_servicio:
                return servicio
        raise ServicioNoDisponibleError(f"No existe servicio con Id '{id_servicio}'")

    def buscar_reserva(self, id_reserva):
        for reserva in self._reservas:
            if reserva.identificador == id_reserva:
                return reserva
        raise ReservaInvalidaError(f"No existe reserva con Id '{id_reserva}'")

    # ---------- clientes ----------
    def registrar_cliente(self, *args, **kwargs):
        """Crea un Cliente y lo agrega a la lista (try/except/else/finally).

        Devuelve el cliente o None si hubo error.
        """
        cliente = None
        try:
            cliente = Cliente(*args, **kwargs)  # las validaciones viven en Cliente
            if any(c.identificador == cliente.identificador for c in self._clientes):
                raise ClienteInvalidoError(
                    f"Cliente '{cliente.identificador}' ya se encuentra registrado")
        except Exception as e:
            logger.error("Falló el registro del cliente: %s", describir_error(e))
            cliente = None
        else:
            self._clientes.append(cliente)
            logger.info("Cliente registrado: %s", cliente.identificador)
        finally:
            logger.debug("Fin de registrar_cliente (total clientes: %d)", len(self._clientes))
        return cliente

    # ---------- servicios ----------
    def registrar_servicio(self, clase_servicio, *args, **kwargs):
        """Crea un servicio (ReservaSala, AlquilerEquipo o AsesoriaEspecializada)."""
        servicio = None
        try:
            if not (isinstance(clase_servicio, type) and issubclass(clase_servicio, Servicio)):
                raise ServicioNoDisponibleError("El tipo de servicio no es válido")
            servicio = clase_servicio(*args, **kwargs)
            if any(s.identificador == servicio.identificador for s in self._servicios):
                raise ServicioNoDisponibleError(f"El servicio '{servicio.identificador}' ya existe")
        except Exception as e:
            logger.error("Creación de servicio fallida: %s", describir_error(e))
            servicio = None
        else:
            self._servicios.append(servicio)
            logger.info("Servicio registrado: %s", servicio.identificador)
        finally:
            logger.debug("Fin de registrar_servicio (total servicios: %d)", len(self._servicios))
        return servicio

    # ---------- reservas ----------
    def _generar_id_reserva(self):
        """Genera un identificador libre con el formato RES-0001, RES-0002..."""
        numero = len(self._reservas) + 1
        while any(r.identificador == f"RES-{numero:04d}" for r in self._reservas):
            numero += 1
        return f"RES-{numero:04d}"

    def crear_reserva(self, id_cliente, id_servicio, duracion, id_reserva=None):
        """Crea una reserva para un cliente y servicio existentes.

        CORRECCIÓN: Reserva(identificador, cliente, servicio, duracion) exige un
        identificador y antes no se le pasaba. Ahora se puede dar uno (id_reserva)
        o, si se omite, se genera automáticamente.

        Usa encadenamiento de excepciones: el error original queda como causa
        del ErrorGestion que se registra en el log.
        """
        reserva = None
        try:
            try:
                cliente = self.buscar_cliente(id_cliente)
                servicio = self.buscar_servicio(id_servicio)
                if id_reserva is None:
                    id_reserva = self._generar_id_reserva()
                elif any(r.identificador == id_reserva for r in self._reservas):
                    raise ReservaInvalidaError(f"La reserva '{id_reserva}' ya existe")
                reserva = Reserva(id_reserva, cliente, servicio, duracion)
            except Exception as e:
                raise ErrorGestion("No fue posible crear la reserva") from e
        except ErrorGestion as e:
            # describir_error recorre toda la cadena __cause__ (ErrorGestion <- causa ...)
            logger.error("%s", describir_error(e))
            reserva = None
        else:
            self._reservas.append(reserva)
            logger.info("Reserva creada: %s (cliente %s, servicio %s)",
                        reserva.identificador, id_cliente, id_servicio)
        finally:
            logger.debug("Fin de crear_reserva (total reservas: %d)", len(self._reservas))
        return reserva

    def confirmar_reserva(self, id_reserva):
        return self._operar_reserva(id_reserva, "confirmar")

    def cancelar_reserva(self, id_reserva):
        return self._operar_reserva(id_reserva, "cancelar")

    def procesar_reserva(self, id_reserva, impuesto=0.0, descuento=0.0):
        # MEJORA: se permite pasar impuesto y descuento (fracciones: 0.19 = 19 %).
        return self._operar_reserva(id_reserva, "procesar",
                                    impuesto=impuesto, descuento=descuento)

    def _operar_reserva(self, id_reserva, accion, **parametros):
        """Ejecuta confirmar/cancelar/procesar de forma segura. Devuelve True/False."""
        try:
            reserva = self.buscar_reserva(id_reserva)
            if accion not in ("confirmar", "cancelar", "procesar"):
                raise OperacionNoPermitidaError(f"Acción '{accion}' no permitida")
            getattr(reserva, accion)(**parametros)
        except Exception as e:
            logger.error("No se pudo %s la reserva '%s': %s", accion, id_reserva, describir_error(e))
            return False
        else:
            logger.info("Reserva '%s': %s realizado", id_reserva, accion)
            return True
        finally:
            logger.debug("Fin de %s reserva", accion)

    # ---------- resumen ----------
    def resumen(self):
        return {
            "clientes": len(self._clientes),
            "servicios": len(self._servicios),
            "reservas": len(self._reservas),
        }
